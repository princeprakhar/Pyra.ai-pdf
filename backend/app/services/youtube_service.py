import uuid
import logging
from urllib.parse import urlparse, parse_qs
from fastapi.responses import JSONResponse
from youtube_transcript_api import YouTubeTranscriptApi

# External dependencies from your project
from app.utils.embedding_utils import embeddings, chunker, pc, index_name
from app.utils.helpers_utils import batch_iterable
from app.utils.rerank_utils import rerank_documents
from app.config import GROQ_API_KEY, OPENAI_API_KEY
from app.models import UserPDF
from groq import Groq
from langchain import hub

def extract_video_id(youtube_url: str) -> str:
    """
    Extracts the video ID from the provided YouTube URL.

    Args:
        youtube_url (str): The full YouTube video URL.

    Returns:
        str: The extracted video ID, or None if extraction fails.
    """
    parsed_url = urlparse(youtube_url)
    # For URLs like: https://www.youtube.com/watch?v=VIDEO_ID
    if parsed_url.hostname in ['www.youtube.com', 'youtube.com']:
        if parsed_url.path == '/watch':
            query_components = parse_qs(parsed_url.query)
            return query_components.get('v', [None])[0]
        # For URLs like: https://www.youtube.com/embed/VIDEO_ID or /v/VIDEO_ID
        if parsed_url.path.startswith("/embed/") or parsed_url.path.startswith("/v/"):
            parts = parsed_url.path.split("/")
            if len(parts) >= 3:
                return parts[2]
    # For shortened URLs like: https://youtu.be/VIDEO_ID
    if parsed_url.hostname == 'youtu.be':
        return parsed_url.path[1:]
    return None

def transcribe_and_translate(youtube_url: str) -> str:
    video_id = extract_video_id(youtube_url)
    if not video_id:
        return "Error: Unable to extract video ID from the provided URL."
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        try:
            # Attempt to retrieve an English transcript (manual preferred over auto-generated)
            transcript = transcript_list.find_transcript(['en'])
        except Exception:
            # Fallback: use the first available transcript
            transcript = list(transcript_list)[0]

        # Translate if transcript is not in English.
        if transcript.language_code != 'en':
            transcript = transcript.translate('en')

        transcript_data = transcript.fetch()
        full_text = " ".join([entry['text'] for entry in transcript_data])
        return full_text

    except Exception as e:
        error_message = f"Error retrieving transcript: {str(e)}"
        logging.error(error_message)
        return error_message
    
async def process_upload_youtube_transcript(youtube_url: str, current_user: UserPDF) -> JSONResponse:
    """
    Processes a YouTube video transcript by performing the following steps:
    1. Extract the video ID.
    2. Retrieve and translate the transcript.
    3. Chunk the transcript text.
    4. Generate embeddings for each chunk.
    5. Upsert the vectors into a Pinecone index under the user's namespace.
    """
    try:
        username = current_user.username
        logging.info(f"Processing YouTube transcript for user: {username}")
        video_id = extract_video_id(youtube_url)
        if not video_id:
            return JSONResponse(
                content={"error": "Unable to extract video ID from URL."},
                status_code=400
            )

        transcript_text = transcribe_and_translate(youtube_url)
        if transcript_text.startswith("Error:"):
            return JSONResponse(
                content={"error": transcript_text},
                status_code=500
            )

        # Chunk the transcript into smaller pieces.
        chunks = chunker.chunk(transcript_text)
        chunked_texts = [chunk.text for chunk in chunks]

        # Generate embeddings for each chunk.
        text_embeddings = embeddings.embed_documents(chunked_texts)

        # Prepare vectors for upsert.
        index = pc.Index(index_name)
        vectors_to_add = [
            {
                "id": f"{video_id}-{uuid.uuid4()}",
                "values": vector,
                "metadata": {
                    "video_id": video_id,
                    "source": youtube_url,
                    "text": chunked_texts[idx],
                    "chunk_index": idx
                }
            }
            for idx, vector in enumerate(text_embeddings)
        ]

        # Upsert vectors in batches.
        batch_size = 200
        for batch in batch_iterable(vectors_to_add, batch_size):
            index.upsert(vectors=batch, namespace=f"{username}_youtube")

        return JSONResponse(
            content={
                "message": "YouTube transcript uploaded and processed successfully!",
                "chunks_processed": len(chunked_texts),
                "video_id": video_id
            },
            status_code=200
        )

    except Exception as e:
        logging.error(f"Error uploading YouTube transcript: {str(e)}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

async def generate_response_youtube_url_query(query: str, video_id: str, current_user: UserPDF) -> JSONResponse:
    """
    Generates an answer for a query using the processed YouTube transcript data stored in Pinecone.

    The process involves:
    1. Embedding the user query.
    2. Querying the Pinecone index for matching transcript chunks (optionally filtered by video ID).
    3. Re-ranking the retrieved documents.
    4. Formatting the context and calling an LLM via Groq to generate the final answer.

    Args:
        query (str): The user’s query.
        video_id (str): The YouTube video ID to filter transcripts (optional).
        current_user (UserPDF): The authenticated user.

    Returns:
        JSONResponse: A response containing the generated answer.
    """
    try:
        username = current_user.username

        # Construct the system message for context.
        system_message = (
            "You are an AI assistant that answers questions using context derived from YouTube "
            "video transcripts. The context is based on processed, chunked, and embedded transcript data. "
            "Answer solely based on the provided context. If details are insufficient, state that you don't have enough information."
        )

        # Embed the query.
        query_vector = embeddings.embed_query(query)
        index = pc.Index(index_name)

        # Optional filtering by video_id.
        filter_dict = {"video_id": video_id} if video_id else None

        fetch_result = index.query(
            vector=query_vector,
            top_k=20,
            include_metadata=True,
            namespace=f"{username}_youtube",
            filter=filter_dict
        )

        # Extract texts from the matched chunks.
        retrieved_texts = [match.metadata["text"] for match in fetch_result.matches]

        # Re-rank the retrieved documents for better relevance.
        reranked_docs = await rerank_documents(query, retrieved_texts)
        context = " ".join([doc['document']['text'] for doc in reranked_docs])

        # Prepare the final prompt.
        formatted_system_message = (
            f"{system_message} Use the following context to answer the question and make sure to cover every aspect of the question. "
        )
        prompt_template = hub.pull("rlm/rag-prompt")
        formatted_prompt = prompt_template.format(context=context, question=query)

        # Initialize the Groq client and generate a completion.
        groq_client = Groq(api_key=GROQ_API_KEY)
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": formatted_system_message},
                {"role": "user", "content": context}
            ],
            model="llama-3.3-70b-versatile",
            max_tokens=4096,
            temperature=0.7,
            stream=False
        )

        response_content = chat_completion.choices[0].message.content

        return JSONResponse(
            content={
                "message": "YouTube query response generated successfully!",
                "response": response_content
            },
            status_code=200
        )

    except Exception as e:
        logging.error(f"Error generating YouTube query response: {str(e)}")
        return JSONResponse(content={"error": str(e)}, status_code=500)



def generate_video_summary(youtube_url: str, current_user: UserPDF) -> JSONResponse:
    """
    Generates a summary of the entire YouTube video transcript.
    
    This function:
    1. Extracts the video ID and retrieves the full transcript.
    2. (Optionally) Could aggregate embeddings from all transcript chunks.
        Here, we use the raw transcript text for summarization.
    3. Constructs a summarization prompt.
    4. Uses the Groq client to generate a summary from an LLM.

    Args:
        youtube_url (str): The full YouTube video URL.
        current_user (UserPDF): The authenticated user.
    
    Returns:
        JSONResponse: A response containing the video summary.
    """
    try:

        transcript_text = transcribe_and_translate(youtube_url)
        if transcript_text.startswith("Error:"):
            return JSONResponse(
                content={"error": transcript_text},
                status_code=500
            )

        # Construct a summarization prompt that uses the entire transcript.
        summarization_prompt = (
            "You are an AI expert in summarization. Please provide a concise and comprehensive summary "
            "of the following YouTube video transcript:\n\n"
            f"{transcript_text}"
        )

        groq_client = Groq(api_key=GROQ_API_KEY)
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a video summarization assistant."},
                {"role": "user", "content": summarization_prompt}
            ],
            model="llama-3.3-70b-versatile",
            max_tokens=512,
            temperature=0.5,
            stream=False
        )
        summary_text = chat_completion.choices[0].message.content

        return JSONResponse(
            content={
                "message": "Video summary generated successfully!",
                "summary": summary_text
            },
            status_code=200
        )
    except Exception as e:
        logging.error(f"Error generating video summary: {str(e)}")
        return JSONResponse(content={"error": str(e)}, status_code=500)
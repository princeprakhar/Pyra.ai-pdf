from urllib.parse import urlparse
from fastapi import UploadFile, HTTPException, status,Query
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy.orm import Session
from app.schemas import ProcessDocRequest, GenerateResponseRequest
from app.models import UserPDF
from app.utils.s3_utils import upload_to_s3, s3_client
from app.utils.embedding_utils import embeddings, chunker, pc, index_name
from app.utils.rerank_utils import rerank_documents
from app.config import S3_BUCKET_NAME
import pymupdf4llm
import os
import tempfile
import uuid
import logging
import aiohttp
from botocore.exceptions import ClientError
from app.utils.helpers import batch_iterable
from app.dependencies.system_message_dependencies import get_latest_system_message
from groq import Groq
from langchain import hub
from openai import OpenAI
from app.config import GROQ_API_KEY,OPENAI_API_KEY



groq_client = Groq(api_key=GROQ_API_KEY)
prompt = hub.pull("rlm/rag-prompt")
client = OpenAI(api_key=OPENAI_API_KEY)



async def generate_response(request: GenerateResponseRequest, current_user: UserPDF, db: Session):
    """
    Generates a text response based on a user query and context retrieved from Pinecone.
    The request is assumed to include a 'pdf_id' field to filter context.
    """
    try:
        logging.info("In the Generate Response")
        query = request.query
        pdf_id = request.pdf_id  # new field for filtering by PDF context
        username = current_user.username
        system_message = ""

        index = pc.Index(index_name)
        query_vector = embeddings.embed_query(query)
        # Now filtering for the current PDF context using pdf_id
        fetch_result = index.query(
            vector=query_vector,
            top_k=5,
            include_metadata=True,
            namespace=username,
            filter={"pdf_id": pdf_id}
        )
        retrieved_texts = [match.metadata["text"] for match in fetch_result.matches]

        reranked_docs = await rerank_documents(query, retrieved_texts)
        context = " ".join([doc['document']['text'] for doc in reranked_docs])

        formatted_system_message = "".join(
            f" {system_message}"
            "You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. "
        )
        logging.info(f"Formatted System Message: {formatted_system_message}")

        formatted_prompt = prompt.format(context=context, question=query)
        logging.info(f"Formatted prompt: {formatted_prompt}")

        chat_completion = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": formatted_system_message
                },
                {
                    "role": "user",
                    "content": formatted_prompt
                }
            ],
            model="llama-3.3-70b-versatile",
            max_tokens=1024,
            temperature=0.7,
            stream=False
        )

        return JSONResponse(
            content={
                "message": "Response generated successfully!",
                "response": chat_completion.choices[0].message.content
            },
            status_code=200
        )

    except Exception as e:
        logging.error(f"Response generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


async def generate_response_audio(pdf_id: str = Query(...), audio_file: UploadFile = None, current_user: UserPDF = None, db: Session = None):
    """
    Generates a response based on an audio file (transcribed to text) and retrieves PDF-specific context.
    The pdf_id is passed as a query parameter.
    """
    try:
        query = None
        logging.info("In the Generate Response Audio")
        username = current_user.username
        system_msg_obj = get_latest_system_message(username, db)
        system_message = system_msg_obj.message if system_msg_obj is not None else ""
        logging.info(f"Current System Message: {system_message}")

        if audio_file:
            with open("temp_audio.mp3", "wb") as buffer:
                buffer.write(await audio_file.read())

            with open("temp_audio.mp3", "rb") as audio:
                transcription = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio
                )
                query = transcription.text
                logging.info(f"Transcribed query: {query}")

        if not query:
            raise HTTPException(status_code=400, detail="No query or audio file provided")

        os.remove("temp_audio.mp3")

        index = pc.Index(index_name)
        query_vector = embeddings.embed_query(query)
        # Filtering results to only include vectors for the given pdf_id
        fetch_result = index.query(
            vector=query_vector,
            top_k=5,
            include_metadata=True,
            namespace=username,
            filter={"pdf_id": pdf_id}
        )
        retrieved_texts = [match.metadata["text"] for match in fetch_result.matches]

        reranked_docs = await rerank_documents(query, retrieved_texts)
        context = " ".join([doc['document']['text'] for doc in reranked_docs])
        logging.info(f"Context: {context}")

        formatted_system_message = "".join(
            f" {system_message}"
            "You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. "
            "If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise."
        )
        logging.info(f"Formatted System Message: {formatted_system_message}")

        formatted_prompt = prompt.format(context=context, question=query)
        logging.info(f"Formatted prompt: {formatted_prompt}")

        chat_completion = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": formatted_system_message
                },
                {
                    "role": "user",
                    "content": formatted_prompt
                }
            ],
            model="llama-3.3-70b-versatile",
            max_tokens=1024,
            temperature=0.7,
            stream=True
        )

        return JSONResponse(
            content={
                "message": "Audio response generated successfully!",
                "response": chat_completion.choices[0].message.content
            },
            status_code=200
        )

    except Exception as e:
        logging.error(f"Response generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


async def upload_doc(file: UploadFile, current_user: UserPDF):
    """
    Uploads a PDF file to S3, processes it to create text chunks, and upserts the embeddings to Pinecone.
    The PDF identifier is stored in the metadata as 'pdf_id' (using the S3 key) for later filtering.
    """
    temp_file_path = None
    username = current_user.username
    try:
        contents = await file.read()
        s3_key = await upload_to_s3(contents, username=username, filename=file.filename, content_type=file.content_type)

        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            temp_file_path = temp_file.name
            s3_client.download_fileobj(
                Bucket=S3_BUCKET_NAME,
                Key=s3_key,
                Fileobj=temp_file
            )

        logging.info(f"Temporary file created at: {temp_file_path}")

        parsed_md_text = pymupdf4llm.to_markdown(temp_file_path)
        created_chunks = chunker.chunk(parsed_md_text)
        chunked_texts = [chunk.text for chunk in created_chunks]
        text_embeddings = embeddings.embed_documents(chunked_texts)

        index = pc.Index(index_name)
        # Each vector now includes a 'pdf_id' field in metadata for filtering during queries.
        vectors_to_add = [
            {
                "id": f"{s3_key}-{uuid.uuid4()}",
                "values": vector,
                "metadata": {
                    "pdf_id": s3_key,        # new metadata field
                    "source": s3_key,
                    "text": chunked_texts[idx],
                    "chunk_index": idx
                }
            }
            for idx, vector in enumerate(text_embeddings)
        ]

        batch_size = 200
        for batch in batch_iterable(vectors_to_add, batch_size):
            index.upsert(vectors=batch, namespace=username)

        return JSONResponse(
            content={
                "message": "File uploaded and processed successfully!",
                "chunks_processed": len(chunked_texts),
                "s3_key": s3_key
            },
            status_code=200
        )

    except Exception as e:
        logging.error(f"Upload error: {str(e)}")
        return JSONResponse(content={"error": str(e)}, status_code=500)
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)
            logging.info(f"Temporary file deleted: {temp_file_path}")         
            
async def get_doc_helper(filename: str, current_user: UserPDF):
    try:
        # Construct the S3 key based on the pattern used in upload_to_s3
        # URL-decode the filename from the path parameter
        logging.info(f"Filename: {filename}")
        from urllib.parse import unquote
        decoded_filename = unquote(filename)
        
        logging.info(f"Decoded filename: {decoded_filename}")
        username = current_user.username
        s3_key = f"uploads/{username}/{decoded_filename}"
        
        logging.info(f"Looking for document with S3 key: {filename}")
        
        try:
            # Check if the object exists in S3
            s3_client.head_object(Bucket=os.getenv("S3_BUCKET_NAME"), Key=s3_key)
            
            # Generate a presigned URL for secure access
            presigned_url = s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': os.getenv("S3_BUCKET_NAME"),
                    'Key': s3_key
                },
                ExpiresIn=3600  # URL expires in 1 hour
            )
            
            return JSONResponse(
                content={
                    "presigned_url": presigned_url,
                    "expires_in": 3600
                },
                status_code=200
            )
            
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                logging.error(f"Document not found in S3: {s3_key}")
                return JSONResponse(
                    content={"error": "Document not found"},
                    status_code=404
                )
            else:
                logging.error(f"S3 error: {str(e)}")
                return JSONResponse(
                    content={"error": "Failed to retrieve document from storage"},
                    status_code=500
                )
            
    except Exception as e:
        logging.error(f"Document retrieval error: {str(e)}")
        return JSONResponse(
            content={"error": str(e)},
            status_code=500
        )
    

async def delete_namespace_vectors_and_pdfs(current_user: UserPDF):
    """
    Deletes all vectors in the Pinecone index for the current user's namespace,
    and deletes all PDF objects stored in the S3 bucket under the user's folder.
    """
    username = current_user.username
    try:
        # Delete all vectors in the user's namespace from Pinecone.
        index = pc.Index(index_name)
        delete_response = index.delete(delete_all=True, namespace=username)
        logging.info(f"Deleted vectors for namespace '{username}', response: {delete_response}")

        # Delete S3 objects in the user's folder.
        # This example assumes that all PDFs are stored under a folder named with the username.
        prefix = f"uploads/{username}/"
        list_response = s3_client.list_objects_v2(Bucket=S3_BUCKET_NAME, Prefix=prefix)
        if 'Contents' in list_response:
            for obj in list_response['Contents']:
                s3_client.delete_object(Bucket=S3_BUCKET_NAME, Key=obj['Key'])
            logging.info(f"Deleted {len(list_response['Contents'])} objects from S3 with prefix '{prefix}'.")
        else:
            logging.info(f"No S3 objects found with prefix '{prefix}'.")

        return JSONResponse(
            content={"message": f"All vectors in namespace '{username}' and associated PDFs in S3 have been deleted."},
            status_code=200
        )
    except Exception as e:
        logging.error(f"Error deleting data for namespace '{username}': {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
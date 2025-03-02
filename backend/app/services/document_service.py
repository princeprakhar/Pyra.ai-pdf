from urllib.parse import urlparse
from fastapi import UploadFile, HTTPException, status
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
from app.utils.helpers import batch_iterable
from app.dependencies.system_message_dependencies import get_latest_system_message
from groq import Groq
from langchain import hub
from openai import OpenAI
from app.config import GROQ_API_KEY,OPENAI_API_KEY



groq_client = Groq(api_key=GROQ_API_KEY)
prompt = hub.pull("rlm/rag-prompt")
client = OpenAI(api_key=OPENAI_API_KEY)

async def process_doc(request: ProcessDocRequest, current_user: UserPDF):
    temp_file_path = None
    username = current_user.username
    try:
        file_path = request.file_path
        index = pc.Index(index_name)

        parsed_url = urlparse(file_path)
        if parsed_url.scheme == "https" and "s3.amazonaws.com" in parsed_url.netloc:
            s3_bucket_name = parsed_url.netloc.split('.')[0]
            s3_key = parsed_url.path.lstrip('/')
        else:
            s3_bucket_name = S3_BUCKET_NAME
            s3_key = file_path

        logging.info(f"S3 Bucket: {s3_bucket_name}, S3 Key: {s3_key}")

        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(s3_key)[1]) as temp_file:
            temp_file_path = temp_file.name
            s3_client.download_fileobj(
                Bucket=s3_bucket_name,
                Key=s3_key,
                Fileobj=temp_file
            )

        logging.info(f"Temporary file created at: {temp_file_path}")

        if not os.path.exists(temp_file_path):
            raise FileNotFoundError(f"Temporary file does not exist: {temp_file_path}")

        parsed_md_text = pymupdf4llm.to_markdown(temp_file_path)
        created_chunks = chunker.chunk(parsed_md_text)
        chunked_texts = [chunk.text for chunk in created_chunks]
        text_embeddings = embeddings.embed_documents(chunked_texts)

        vectors_to_add = [
            {
                "id": f"{s3_key}-{uuid.uuid4()}",
                "values": vector,
                "metadata": {
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

        logging.info(f"Document processed successfully: {file_path}")
        return JSONResponse(
            content={"message": "Document processed successfully!", "chunks_processed": len(chunked_texts)},
            status_code=200
        )

    except Exception as e:
        logging.error(f"Document processing error: {str(e)}")
        return JSONResponse(content={"error": str(e)}, status_code=500)
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)
            logging.info(f"Temporary file deleted: {temp_file_path}")

async def generate_response(request: GenerateResponseRequest, current_user: UserPDF, db: Session):
    try:
        logging.info("In the Generate Response")
        query = request.query
        username = current_user.username
        # system_message = get_latest_system_message(username, db).message if not get_latest_system_message(username, db) else None
        # logging.info(f"Current System Message: {system_message}")
        system_message = ""

        index = pc.Index(index_name)
        query_vector = embeddings.embed_query(query)
        fetch_result = index.query(
            vector=query_vector,
            top_k=5,
            include_metadata=True,
            namespace=username
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
            content={"message": "Response generated successfully!", "response": chat_completion.choices[0].message.content},
            status_code=200
        )

    except Exception as e:
        logging.error(f"Response generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def generate_response_audio(audio_file: UploadFile, current_user: UserPDF, db: Session):
    try:
        query = None
        logging.info("In the Generate Response Audio")
        username = current_user.username
        system_message = get_latest_system_message(username, db).message if get_latest_system_message(username, db) is not None else ""
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
        fetch_result = index.query(
            vector=query_vector,
            top_k=5,
            include_metadata=True,
            namespace=username
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
            content={"message": "Audio response generated successfully!", "response": chat_completion.choices[0].message.content},
            status_code=200
        )

    except Exception as e:
        logging.error(f"Response generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def upload_doc(file: UploadFile, current_user: UserPDF):
    temp_file_path = None
    username = current_user.username
    try:
        contents = await file.read()
        s3_key = await upload_to_s3(contents,username=username, filename=file.filename, content_type=file.content_type)

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
        vectors_to_add = [
            {
                "id": f"{s3_key}-{uuid.uuid4()}",
                "values": vector,
                "metadata": {
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

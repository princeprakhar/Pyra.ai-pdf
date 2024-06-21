import os
import io 
import base64
import re
import whisper
from pytube import YouTube
from pydub import AudioSegment
import time

from typing import Optional
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Request, Form, File, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema.document import Document
from langchain_pinecone import PineconeVectorStore
from pinecone.grpc import PineconeGRPC as Pinecone
from pinecone import ServerlessSpec
from langchain_community.llms import Ollama
from langchain_community.embeddings import OllamaEmbeddings

# Initialize FastAPI application
app = FastAPI()

# Mount static files directory and initializing the Jinja2 templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Loading the embedding model and whisper model
embedding_model = OllamaEmbeddings(model="jina/jina-embeddings-v2-base-de")
whisper_model = whisper.load_model("base")

def setup_pinecone(index_name):
    # Initialize Pinecone client
    pc = Pinecone(api_key=os.environ['PINECONE_API_KEY'])
    
    if index_name in pc.list_indexes().names():
        pc.delete_index(index_name)
        # Wait for the deletion to complete
        time.sleep(2)  

    # Retry logic to ensure the index is properly deleted before recreating
    retries = 0
    while index_name in pc.list_indexes().names() and retries < 5:
        time.sleep(1)  # Waiting for 1 second before retrying
        retries += 1

    # Creating a new index
    pc.create_index(
        name=index_name,
        dimension=768,
        metric="cosine",
        spec=ServerlessSpec(
            cloud='aws',
            region='us-east-1'
        )
    )
    
    # Add a delay or retry logic to wait for the index to be created
    retries = 0
    while index_name not in pc.list_indexes().names() and retries < 5:
        time.sleep(1)  # Wait for 1 second
        retries += 1

    if index_name not in pc.list_indexes().names():
        raise ValueError(f"Failed to create index '{index_name}'")


# Function to process PDF data and return success message and Pinecone object
def split_load_data(pdf_data, index_name, embedding_model):
    file_object = io.BytesIO(pdf_data)
    reader = PdfReader(file_object)

    pdf_text = ""
    for page in reader.pages:
        pdf_text += page.extract_text()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    docs = [Document(page_content=x) for x in text_splitter.split_text(pdf_text)]

    # Calling the function to setup vector database
    setup_pinecone("docquest")
    pinecone = PineconeVectorStore.from_documents(
        docs, embedding_model, index_name=index_name, pinecone_api_key=os.environ['PINECONE_API_KEY']
    )

    success_message = "Document has been processed and stored in Vector database"
    return success_message, pinecone


# Function to extract the video ID from the YouTube URL
def get_youtube_id(url: str) -> str:
    regex = r"(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})"
    match = re.match(regex, url)
    if match:
        return match.group(1)
    else:
        raise ValueError("Invalid YouTube URL")
    

# Function to download and convert YouTube audio to a temporary file for transcription
def download_and_convert_audio(video_url: str, output_path: str) -> str:
    yt = YouTube(video_url)
    audio_stream = yt.streams.filter(only_audio=True).first()
    audio_file = audio_stream.download(output_path=output_path)
    audio_wav = os.path.splitext(audio_file)[0] + '.wav'
    
    # Convert the downloaded audio file to WAV format using pydub
    audio = AudioSegment.from_file(audio_file)
    audio.export(audio_wav, format="wav")
    
    # Remove the original audio file
    os.remove(audio_file)

    return audio_wav


# Function to transcribe audio using OpenAI's Whisper model
def transcribe_audio(whisper_model, file_path: str) -> str:
    result = whisper_model.transcribe(file_path)
    return result["text"]


# Route to render home.html
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


# Route to render chat_with_pdf.html for GET request
@app.get("/chat_with_pdf", response_class=HTMLResponse)
async def get_chat_with_pdf(request: Request):
    return templates.TemplateResponse("chat_with_pdf.html", {"request": request})


# Route to handle PDF upload and processing for POST request
@app.post("/chat_with_pdf", response_class=HTMLResponse)
async def post_chat_with_pdf(request: Request, file: UploadFile = File(...), additional_text: Optional[str] = Form(None)):
    pdf_data = await file.read()
    b64_pdf = base64.b64encode(pdf_data).decode("utf-8")
    pdf_display = f'data:application/pdf;base64,{b64_pdf}'

    # Call split_load_data function to process PDF and retrieve success message and Pinecone object
    success_message, pinecone = split_load_data(pdf_data, "docquest", embedding_model)

    # Prepare context text for Pinecone operation if additional_text is provided
    context_text = ""
    if additional_text:
        result_text = pinecone.similarity_search(additional_text)[:1]
        if result_text:
            context_text = result_text[0].page_content

    return templates.TemplateResponse("chat_with_pdf.html", {
        "request": request,
        "pdf_display": pdf_display,
        "result": success_message,
        "additional_text": additional_text,
        "context_text": context_text
    })


# Route to render chat_with_youtube.html for GET request
@app.get("/chat_with_youtube", response_class=HTMLResponse)
async def get_chat_with_youtube(request: Request):
    return templates.TemplateResponse("chat_with_youtube.html", {"request": request})


# Route to handle YouTube URL processing for POST request
@app.post("/chat_with_youtube", response_class=HTMLResponse)
async def post_chat_with_youtube(request: Request, url: str = Form(...)):
    try:
        # Extracting the YouTube Video ID
        video_id = get_youtube_id(url)
        
        # Downloading and converting the YouTube video audio
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        output_path = "download_video"  
        audio_file = download_and_convert_audio(video_url, output_path)
        
        # Transcribing the audio
        transcription = transcribe_audio(whisper_model, audio_file)
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        docs = [Document(page_content=x) for x in text_splitter.split_text(transcription)]
        
        # Calling the function to setup vector database
        setup_pinecone("ragvideo")
        pinecone = PineconeVectorStore.from_documents(
            docs, embedding_model, index_name="ragvideo", pinecone_api_key=os.environ['PINECONE_API_KEY']
        )
        
        # Clean up the converted audio file
        os.remove(audio_file)
        
        # Return success message along with video_id and transcription
        success_message = f"Video '{video_id}' processed and stored in vector database successfully."
        return templates.TemplateResponse("chat_with_youtube.html", {
            "request": request,
            "video_id": video_id,
            "transcription": transcription,
            "success_message": success_message
        })
    
    except ValueError as e:
        # If the URL is invalid, return an error message
        return templates.TemplateResponse("chat_with_youtube.html", {"request": request, "error": str(e)})
    
    except Exception as e:
        # Handle other errors (e.g., download/transcription errors)
        return templates.TemplateResponse("chat_with_youtube.html", {"request": request, "error": "An error occurred: " + str(e)})



# Run the application with uvicorn server
if __name__ == '__main__':
    import uvicorn
    
    # Start the FastAPI application using uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

import time
import os
import io 
import base64

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

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize Jinja2 templates
templates = Jinja2Templates(directory="templates")

def load_models():
    embedding_model = OllamaEmbeddings(model="jina/jina-embeddings-v2-base-de")
    
    # Setup for Pinecone vector database
    pc = Pinecone(api_key=os.environ['PINECONE_API_KEY'])
    index_name = "docquest"

    if index_name in pc.list_indexes().names():
        pc.delete_index(index_name)
        # Wait for the deletion to complete
        time.sleep(2)  # Adjust delay as necessary

    # Retry logic to ensure the index is properly deleted before recreating
    retries = 0
    while index_name in pc.list_indexes().names() and retries < 5:
        time.sleep(2)  # Wait for 2 seconds before retrying
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
        time.sleep(2)  # Wait for 2 seconds
        retries += 1

    if index_name not in pc.list_indexes().names():
        raise ValueError(f"Failed to create index '{index_name}'")

    return embedding_model

# Load models when the application starts
embedding_model = load_models()

# Function to process PDF data and return success message and Pinecone object
def split_load_data(pdf_data, index_name, embedding_model):
    file_object = io.BytesIO(pdf_data)
    reader = PdfReader(file_object)

    pdf_text = ""
    for page in reader.pages:
        pdf_text += page.extract_text()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    docs = [Document(page_content=x) for x in text_splitter.split_text(pdf_text)]

    pinecone = PineconeVectorStore.from_documents(
        docs, embedding_model, index_name=index_name, pinecone_api_key=os.environ['PINECONE_API_KEY']
    )

    success_message = "Document has been processed and stored in Vector database"
    return success_message, pinecone

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
async def post_chat_with_pdf(request: Request, file: UploadFile = File(...)):
    pdf_data = await file.read()
    b64_pdf = base64.b64encode(pdf_data).decode("utf-8")
    pdf_display = f'data:application/pdf;base64,{b64_pdf}'

    # Call split_load_data function to process PDF and retrieve success message and Pinecone object
    success_message, pinecone = split_load_data(pdf_data, "docquest", embedding_model)

    return templates.TemplateResponse("chat_with_pdf.html", {"request": request, "pdf_display": pdf_display, "result": success_message})

# Route to render chat_with_youtube.html for GET request
@app.get("/chat_with_youtube", response_class=HTMLResponse)
async def get_chat_with_youtube(request: Request):
    return templates.TemplateResponse("chat_with_youtube.html", {"request": request})

# Route to handle YouTube URL processing for POST request
@app.post("/chat_with_youtube", response_class=HTMLResponse)
async def post_chat_with_youtube(request: Request, url: str = Form(...)):
    # Handle YouTube chat logic here
    return templates.TemplateResponse("chat_with_youtube.html", {"request": request, "result": "YouTube video processed"})

# Run the application with uvicorn server
if __name__ == '__main__':
    # Run load_models() on application start
    load_models()
    # Start the FastAPI application using uvicorn
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

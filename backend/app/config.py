import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("CALLBACK_URL")
FRONTEND_URL = "http://localhost:3000"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
JINA_API_KEY = os.getenv("JINA_API_KEY")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
DATABASE_URL = os.getenv("DATABASE_CONNECTION")
BLANDAI_API_KEY = os.getenv("BLANDAI_API_KEY")
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7
BLANDAI_API_KEY = os.getenv("BLANDAI_API_KEY")

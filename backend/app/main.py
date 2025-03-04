from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from app.routes import auth_routes, user_routes, document_routes, system_message_routes
from app.middlewares.logging_middleware import log_requests
from app.config import SECRET_KEY, DATABASE_URL
from app.database import engine, Base
import logging
import numpy as np

import warnings

warnings.filterwarnings("ignore", category=RuntimeWarning)

# Initialize FastAPI app
app = FastAPI()

# Add middleware
app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY,
    session_cookie="session_cookie",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://prakhar-ai-pdf.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.middleware("http")(log_requests)

# Include routers
app.include_router(auth_routes.router)
app.include_router(user_routes.router)
app.include_router(document_routes.router)
app.include_router(system_message_routes.router)

@app.get("/")
async def root():
    return {"status": "healthy"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Database connection and table creation
@app.on_event("startup")
async def startup_event():
    logging.info("Startup event triggered")
    try:
        # Ensure the database engine is correctly initialized
        if engine.url.database:
            Base.metadata.create_all(bind=engine)
            logging.info("Database connection and tables created successfully!")
        else:
            raise ValueError("Database URL is not set correctly.")
    except Exception as e:
        logging.error(f"Failed to make database connection. Error: {e}")
        raise

# Ensure logging is configured
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def some_function():
    # Example operation
    try:
        result = np.exp2(some_value)  # Replace some_value with your variable
        logging.debug(f"Result: {result}")
    except Exception as e:
        logging.error(f"Error encountered: {e}")

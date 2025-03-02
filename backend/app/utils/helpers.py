from app.models import SystemMessagePDF,UserPDF
import itertools
import aiohttp
from fastapi.exceptions import HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from langchain import hub
from app.config import JINA_API_KEY



prompt = hub.pull("rlm/rag-prompt")

# Utility functions
def batch_iterable(iterable, batch_size=200):
    """Break an iterable into chunks of size batch_size."""
    it = iter(iterable)
    chunk = tuple(itertools.islice(it, batch_size))
    while chunk:
        yield chunk
        chunk = tuple(itertools.islice(it, batch_size))

        
def get_latest_system_message(username,db: Session):
    latest_message = db.query(SystemMessagePDF).filter(
        SystemMessagePDF.username == username
    ).order_by(
        SystemMessagePDF.timestamp.desc()
    ).first()

    return latest_message



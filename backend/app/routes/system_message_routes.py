from fastapi import APIRouter, Depends, Body, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.schemas import SystemMessageRequest
from app.dependencies.auth_dependencies import get_current_user
from app.dependencies.db_dependencies import get_db
from app.models import UserPDF
from app.services.system_message_service import save_system_message

router = APIRouter()

@router.post("/api/system-message")
async def save_system_message_route(request: SystemMessageRequest, current_user: UserPDF = Depends(get_current_user), db: Session = Depends(get_db)):
    return save_system_message(request, current_user, db)

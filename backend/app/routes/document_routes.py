from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status,Query
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy.orm import Session
from app.schemas import ProcessDocRequest, GenerateResponseRequest, GetDocRequest
from app.dependencies.auth_dependencies import get_current_user
from app.dependencies.db_dependencies import get_db
from app.models import UserPDF
from app.services.document_service import process_doc, generate_response, generate_response_audio, upload_doc,get_doc_helper
import logging

router = APIRouter()

# @router.post("/api/process-doc")
# async def process_doc_route(request: ProcessDocRequest, current_user: UserPDF = Depends(get_current_user)):
#     return await process_doc(request, current_user)

@router.post("/api/generate-response")
async def generate_response_route(request: GenerateResponseRequest, current_user: UserPDF = Depends(get_current_user), db: Session = Depends(get_db)):
    return await generate_response(request, current_user, db)

@router.post("/api/generate-response-audio")
async def generate_response_audio_route(audio_file: UploadFile = File(...), current_user: UserPDF = Depends(get_current_user), db: Session = Depends(get_db)):
    logging.info(f"{current_user}")
    return await generate_response_audio(audio_file, current_user, db)

@router.post("/api/upload-doc")
async def upload_doc_route(file: UploadFile = File(...), current_user: UserPDF = Depends(get_current_user)):
    return await upload_doc(file, current_user)



@router.get("/api/get-doc/")
async def get_doc_route(filename: str = Query(..., min_length=1), current_user: UserPDF = Depends(get_current_user)):
    return await get_doc_helper(filename=filename, current_user=current_user)


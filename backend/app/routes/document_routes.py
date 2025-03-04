from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status,Query
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy.orm import Session
from app.schemas import ProcessDocRequest, GenerateResponseRequest, GetDocRequest
from app.dependencies.auth_dependencies import get_current_user
from app.dependencies.db_dependencies import get_db
from app.models import UserPDF
from app.services.document_service import generate_response, generate_response_audio, upload_doc,get_doc_helper,delete_namespace_vectors_and_pdfs
import logging

router = APIRouter()

@router.post("/api/generate-response")
async def generate_response_route(request: GenerateResponseRequest, current_user: UserPDF = Depends(get_current_user), db: Session = Depends(get_db)):
    return await generate_response(request, current_user, db)

@router.post("/api/generate-response-audio")
async def generate_response_audio_route(pdf_id: str = Query(...),audio_file: UploadFile = File(...), current_user: UserPDF = Depends(get_current_user), db: Session = Depends(get_db)):
    logging.info(f"{current_user}")
    return await generate_response_audio(pdf_id,audio_file, current_user, db)

@router.post("/api/upload-doc")
async def upload_doc_route(file: UploadFile = File(...), current_user: UserPDF = Depends(get_current_user)):
    return await upload_doc(file, current_user)



@router.get("/api/get-doc/")
async def get_doc_route(filename: str = Query(..., min_length=1), current_user: UserPDF = Depends(get_current_user)):
    return await get_doc_helper(filename=filename, current_user=current_user)

@router.delete("/api/namespace-data", status_code=200)
async def delete_vectors_and_pdf_route(current_user: UserPDF = Depends(get_current_user)):
    """
    Endpoint to delete all vectors in the Pinecone index for the current user's namespace.
    """
    return await delete_namespace_vectors_and_pdfs(current_user)
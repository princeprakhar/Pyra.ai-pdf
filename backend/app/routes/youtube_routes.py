from fastapi import APIRouter, Depends, HTTPException, status,Query
from app.schemas import YoutubeRequest, YoutubeQueryRequest
from app.services.youtube_service import (
    process_upload_youtube_transcript ,
    generate_response_youtube_url_query,
    generate_video_summary
)
from app.dependencies.auth_dependencies import get_current_user
from app.models import UserPDF
import logging

router = APIRouter(prefix="/api/youtube", tags=["YouTube"])

@router.post("/upload", status_code=status.HTTP_200_OK)
async def upload_youtube_transcript_handler(
    request: YoutubeRequest,
    current_user: UserPDF = Depends(get_current_user)
):
    """
    Endpoint for processing and uploading a YouTube video transcript.
    """
    try:
        logging.info("In the upload_youtube_transcript_handler")
        response = await process_upload_youtube_transcript(request.youtube_url, current_user)
        return response
    except Exception as error:
        logging.error(f"Error in upload_youtube_transcript_handler: {error}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/transcript", status_code=status.HTTP_200_OK)
def get_youtube_transcript_handler(
    youtube_url: str = Query(...), 
    current_user: UserPDF = Depends(get_current_user)
):
    """
    Get a YouTube transcript using a query parameter instead of request body.
    """
    try:
        return generate_video_summary(youtube_url, current_user)
    except Exception as error:
        logging.error(f"Error in get_youtube_transcript_handler: {error}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/query", status_code=status.HTTP_200_OK)
async def query_youtube_transcript_handler(
    query: str = Query(...), 
    video_id: str = Query(...),
    current_user: UserPDF = Depends(get_current_user)
):
    """
    Query a YouTube video transcript using query parameters.
    """
    try:
        return await generate_response_youtube_url_query(
            query=query,
            video_id=video_id,
            current_user=current_user
        )
    except Exception as error:
        logging.error(f"Error in query_youtube_transcript_handler: {error}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
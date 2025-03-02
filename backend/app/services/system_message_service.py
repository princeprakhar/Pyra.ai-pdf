from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.schemas import SystemMessageRequest
from app.models import SystemMessagePDF,UserPDF

def save_system_message(request: SystemMessageRequest, current_user: UserPDF, db: Session):
    try:
        system_message = request.system_message
        username = current_user.username
        db_system_message = SystemMessagePDF(message=system_message, username=username)
        try:
            db.add(db_system_message)
            db.commit()
            db.refresh(db_system_message)
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=str(e))
        return JSONResponse(content={"Saved System Message for the username": username}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

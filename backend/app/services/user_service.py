from sqlalchemy.orm import Session
from app.models import UserPDF
from app.schemas import SignupRequest
from fastapi import HTTPException, status
from email_validator import validate_email, EmailNotValidError

def validate_signup_data(signup_request: SignupRequest, db: Session) -> None:
    if db.query(UserPDF).filter(UserPDF.username == signup_request.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    if db.query(UserPDF).filter(UserPDF.email == signup_request.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    try:
        validate_email(signup_request.email)
    except EmailNotValidError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email format"
        )

    if not any(c.isupper() for c in signup_request.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must contain at least one uppercase letter"
        )
    if not any(c.islower() for c in signup_request.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must contain at least one lowercase letter"
        )
    if not any(c.isdigit() for c in signup_request.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must contain at least one number"
        )



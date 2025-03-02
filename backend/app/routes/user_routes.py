from fastapi import APIRouter, Depends, Body, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas import SignupRequest, UserResponse
from app.auth import get_password_hash
from app.models import UserPDF
from app.dependencies.db_dependencies import get_db
from app.services.user_service import validate_signup_data

router = APIRouter()

@router.post("/api/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(signup_request: SignupRequest = Body(...), db: Session = Depends(get_db)):
    validate_signup_data(signup_request, db)

    hashed_password = get_password_hash(signup_request.password)
    db_user = UserPDF(
        username=signup_request.username,
        hashed_password=hashed_password,
        email=signup_request.email,
        full_name=signup_request.full_name
    )

    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating user"
        )

    return UserResponse(
        username=db_user.username,
        email=db_user.email,
        full_name=db_user.full_name
    )

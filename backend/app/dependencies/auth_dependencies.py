from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app.models import UserPDF
from app.dependencies.db_dependencies import get_db
from app.config import SECRET_KEY
from typing import Optional
from app.auth import get_password_hash
import logging
from google.oauth2 import id_token as google_id_token
from google.auth.transport import requests as google_requests
from app.config import GOOGLE_CLIENT_ID
from app.schemas import TokenData

ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> UserPDF:
    """
    This dependency first attempts to validate the token as a server-generated JWT.
    If that fails (JWTError is raised), it then tries to validate it as a Google ID token.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # First, try to decode as a traditional JWT (server issued)
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
        user = get_user(db, username=token_data.username)
        if user is None:
            raise credentials_exception
        return user
    except JWTError:
        # If traditional JWT validation fails, try to validate as a Google token
        try:
            req = google_requests.Request()
            # This verifies the Google token's signature, expiration, and audience
            google_payload = google_id_token.verify_oauth2_token(token, req, GOOGLE_CLIENT_ID)
            # For Google tokens, you might use the user's email as the unique identifier
            google_username = google_payload.get("email")
            logging.info(f"Email:{google_username}")
            if google_username is None:
                raise credentials_exception
            user = get_user(db, username=google_username)
            if user is None:
                raise credentials_exception
            return user
        except ValueError:
            raise credentials_exception



def get_user(db: Session, username: str) -> Optional[UserPDF]:
    return db.query(UserPDF).filter(UserPDF.username == username).first()


def insert_user_to_db(
    username: str,
    email: str,
    full_name: str,
    password: str,
    db: Session  # No default dependency here
):
    hashed_password = get_password_hash(password)
    db_user = UserPDF(
        username=username,
        hashed_password=hashed_password,
        email=email,
        full_name=full_name
    )
    
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return {"message": "User added successfully"}
    except Exception as e:
        db.rollback()
        raise Exception(f"Error: {e}")
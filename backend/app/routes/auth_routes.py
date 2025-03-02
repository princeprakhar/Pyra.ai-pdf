from fastapi import APIRouter, Depends, Request, Body, HTTPException, status
from fastapi.responses import RedirectResponse
from app.schemas import SigninRequest, Token
from app.auth import authenticate_user, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from app.dependencies.auth_dependencies import get_current_user,get_user,insert_user_to_db
from app.models import UserPDF
from sqlalchemy.orm import Session
from app.config import GOOGLE_REDIRECT_URI, FRONTEND_URL,GOOGLE_CLIENT_ID,GOOGLE_CLIENT_SECRET
from authlib.integrations.starlette_client import OAuth
from app.dependencies.db_dependencies import get_db
from datetime import timedelta
import logging


router = APIRouter()

oauth = OAuth()
oauth.register(
    name="google",
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    authorize_url="https://accounts.google.com/o/oauth2/auth",
    access_token_url="https://oauth2.googleapis.com/token",
    api_base_url="https://www.googleapis.com/oauth2/v2/",
    client_kwargs={"scope": "openid email profile"},
    userinfo_endpoint="https://openidconnect.googleapis.com/v1/userinfo",
    jwks_uri="https://www.googleapis.com/oauth2/v3/certs"
)

@router.post("/api/signin", response_model=Token)
async def signin(signin_request: SigninRequest = Body(...),db:Session = Depends(get_db)):
    logging.info(f"Username: {signin_request.username} Password:{signin_request.password}")
    user = authenticate_user(db,username=signin_request.username, password=signin_request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    return Token(access_token=access_token, token_type="bearer")

@router.get("/api/google")
async def google_login(request: Request):
    redirect_uri = GOOGLE_REDIRECT_URI
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/api/google/callback")
async def google_callback(request: Request,db:Session=Depends(get_db)):
    logging.info("In the callback function")
    token = await oauth.google.authorize_access_token(request)

    if "id_token" not in token:
        raise ValueError("Missing 'id_token' in Google's response")

    id_token = token["id_token"]
    user_info = token["userinfo"]
    email = user_info["email"]
    username = user_info["email"]
    hash_password = user_info["at_hash"]
    full_name = user_info["name"]
    if get_user(db,username=username) is None:
        db_user = insert_user_to_db(db=db,username=username, email=email, full_name=full_name, password=hash_password)
        logging.info(f"User saved to Database Successfully : {db_user}")

    frontend_redirect_url = f"{FRONTEND_URL}?access_token={id_token}"
    return RedirectResponse(frontend_redirect_url)

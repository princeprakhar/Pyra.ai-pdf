from fastapi import APIRouter, Depends, Request, Body, HTTPException, status
from fastapi.responses import RedirectResponse,JSONResponse
from app.schemas import SigninRequest, Token
from app.auth import authenticate_user, create_access_token, create_refresh_token
from app.dependencies.auth_dependencies import get_current_user,get_user,insert_user_to_db
from app.models import UserPDF
from sqlalchemy.orm import Session
from app.config import GOOGLE_REDIRECT_URI, FRONTEND_URL,GOOGLE_CLIENT_ID,GOOGLE_CLIENT_SECRET
from authlib.integrations.starlette_client import OAuth
from app.dependencies.db_dependencies import get_db
from datetime import timedelta
import logging
from jose import JWTError, jwt
from app.config import SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS

router = APIRouter(prefix = "/api/auth",tags=["Auth"])

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

@router.post("/signin", response_model=Token)
async def signin(signin_request: SigninRequest = Body(...), db: Session = Depends(get_db)):
    logging.info(f"Username: {signin_request.username} Password:{signin_request.password}")
    
    user = authenticate_user(db, username=signin_request.username, password=signin_request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    access_token = create_access_token({"sub": user.username}, access_token_expires)
    refresh_token = create_refresh_token({"sub": user.username}, refresh_token_expires)
    logging.info(f"{refresh_token}")

    response = JSONResponse(content={"access_token": access_token, "token_type": "bearer"})
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,  # Prevent JavaScript access
        secure=True,    # Send only over HTTPS
        samesite="Lax"
    )

    return response

@router.post("/refresh")
async def refresh_access_token(request: Request):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token missing")

    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=["HS256"])
        username: str = payload.get("sub")
        if not username:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

        new_access_token = create_access_token({"sub": username}, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
        return {"access_token": new_access_token, "token_type": "bearer"}

    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

@router.post("/logout")
async def logout():
    response = JSONResponse(content={"message": "Logged out"})
    response.delete_cookie("refresh_token")
    return response

@router.get("/google")
async def google_login(request: Request):
    redirect_uri = GOOGLE_REDIRECT_URI
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/google/callback")
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



from pydantic import BaseModel
from typing import Optional

class SigninRequest(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None

class UserResponse(BaseModel):
    username: str
    email: str
    full_name: str

class SignupRequest(BaseModel):
    username: str
    email: str
    full_name: str
    password: str

class SystemMessageRequest(BaseModel):
    system_message: str

class ProcessDocRequest(BaseModel):
    file_path: str

class GenerateResponseRequest(BaseModel):
    query: str

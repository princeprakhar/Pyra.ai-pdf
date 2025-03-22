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
    pdf_id: str
    
class GetDocRequest(BaseModel):
    filename: str

class YoutubeRequest(BaseModel):
    youtube_url: str

class YoutubeQueryRequest(BaseModel):
    query: str
    video_id: str


class MakeCallRequest(BaseModel):
    objective: str
    context: str
    caller_number: str
    caller_name: str
    caller_email: str
    language_code: str
    phone_number: str
    name_of_org: str


class CallDetailRequest(BaseModel):
    pass
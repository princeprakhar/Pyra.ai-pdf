from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class UserPDF(Base):
    __tablename__ = "users_pdf"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    email = Column(String, unique=True, index=True)
    full_name = Column(String)
    created_at = Column(DateTime, index=True,default = datetime.now())
    updated_at = Column(DateTime, index=True,default = datetime.now() )

class SystemMessagePDF(Base):
    __tablename__ = "system_messages_pdf"
    id = Column(Integer, primary_key=True, index=True)
    message = Column(String)
    username = Column(String, index=True)
    timestamp = Column(DateTime, index=True)
    avtar_name = Column(String,unique = True)

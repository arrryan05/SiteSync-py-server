from pydantic import BaseModel, EmailStr
from typing import Optional

class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    name: Optional[str]

class SignupResponse(BaseModel):
    user_id: str
    email: EmailStr
    name: Optional[str]
    token: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    user_id: str
    email: EmailStr
    name: Optional[str]
    token: str

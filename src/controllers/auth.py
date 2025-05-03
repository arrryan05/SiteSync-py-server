# src/controllers/auth.py

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from db.database import get_session
from schemas.auth import SignupRequest, SignupResponse, LoginRequest, LoginResponse
from services.auth import signup, login

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=SignupResponse)
def signup_controller(
    data: SignupRequest,
    session: Session = Depends(get_session),
):
    try:
        return signup(data, session)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=LoginResponse)
def login_controller(
    data: LoginRequest,
    session: Session = Depends(get_session),
):
    try:
        return login(data, session)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

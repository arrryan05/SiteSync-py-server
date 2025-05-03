from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.auth import SignupRequest, LoginRequest, SignupResponse, LoginResponse
from services.auth import signup_service, login_service
from db.database import get_session

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=SignupResponse)
async def signup(
    payload: SignupRequest,
    session: AsyncSession = Depends(get_session),
):
    try:
        return await signup_service(payload, session)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=LoginResponse)
async def login(
    payload: LoginRequest,
    session: AsyncSession = Depends(get_session),
):
    try:
        return await login_service(payload, session)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

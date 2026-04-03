import bcrypt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from db.models import User
from schemas.auth import SignupRequest, SignupResponse, LoginRequest, LoginResponse
from utils.jwt import create_access_token


async def signup_service(
    data: SignupRequest, session: AsyncSession
) -> SignupResponse:
    # 1️⃣ Check if user exists
    stmt = select(User).where(User.email == data.email)
    existing = (await session.execute(stmt)).scalar_one_or_none()
    if existing:
        raise ValueError("User already exists")

    # 2️⃣ Hash password
    hashed_pw = bcrypt.hashpw(
        data.password.encode(), bcrypt.gensalt()
    ).decode()

    # 3️⃣ Create user
    user = User(email=data.email, name=data.name, hashed_password=hashed_pw)
    session.add(user)
    await session.commit()
    await session.refresh(user)

    # 4️⃣ Issue JWT
    token = create_access_token({"user_id": user.id})
    return SignupResponse(
        user_id=user.id, email=user.email, name=user.name, token=token
    )


async def login_service(
    data: LoginRequest, session: AsyncSession
) -> LoginResponse:
    stmt = select(User).where(User.email == data.email)
    user = (await session.execute(stmt)).scalar_one_or_none()
    if not user or not user.hashed_password:
        raise ValueError("Invalid credentials")

    if not bcrypt.checkpw(data.password.encode(), user.hashed_password.encode()):
        raise ValueError("Invalid credentials")

    token = create_access_token({"user_id": user.id})
    return LoginResponse(
        user_id=user.id, email=user.email, name=user.name, token=token
    )

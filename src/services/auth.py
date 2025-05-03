# # src/services/auth.py

# from sqlmodel import Session, select
# from db.models import User
# from schemas.auth import SignupRequest, SignupResponse, LoginRequest, LoginResponse
# import bcrypt
# from utils.jwt import create_access_token


# def signup(data: SignupRequest, session: Session) -> SignupResponse:
#     # 1️⃣ Check if user exists
#     statement = select(User).where(User.email == data.email)
#     existing_user = session.exec(statement).first()
#     if existing_user:
#         raise ValueError("User already exists")

#     # 2️⃣ Hash the password
#     hashed_pw = bcrypt.hashpw(data.password.encode(), bcrypt.gensalt()).decode()

#     # 3️⃣ Create & persist the user
#     user = User(email=data.email, name=data.name, hashed_password=hashed_pw)
#     session.add(user)
#     session.commit()
#     session.refresh(user)

#     # 4️⃣ Issue a JWT
#     token = create_access_token({"user_id": user.id})

#     return SignupResponse(
#         user_id=user.id,
#         email=user.email,
#         name=user.name,
#         token=token
#     )


# def login(data: LoginRequest, session: Session) -> LoginResponse:
#     # 1️⃣ Look up the user
#     statement = select(User).where(User.email == data.email)
#     user = session.exec(statement).first()
#     if not user or not user.hashed_password:
#         raise ValueError("Invalid credentials")

#     # 2️⃣ Verify the password
#     if not bcrypt.checkpw(data.password.encode(), user.hashed_password.encode()):
#         raise ValueError("Invalid credentials")

#     # 3️⃣ Issue a JWT
#     token = create_access_token({"user_id": user.id})

#     return LoginResponse(
#         user_id=user.id,
#         email=user.email,
#         name=user.name,
#         token=token
#     )

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

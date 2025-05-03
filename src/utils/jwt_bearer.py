# utils/jwt_bearer.py
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from .jwt import verify_token  

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
    )
    try:
        payload = verify_token(token)
    except JWTError:
        raise credentials_exception

    # map whatever the JWT gave you onto "userId"
    user_id = payload.get("userId") or payload.get("user_id")
    if not user_id:
        raise credentials_exception

    return {"userId": user_id}

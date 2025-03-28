from fastapi import APIRouter, Depends, HTTPException
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from src.database.db import get_db
from src.schemas.users import UserCreate, UserResponse, Token
from src.auth import handlers, jwt
from src.services.redis_client import get_redis

router = APIRouter(tags=["Auth"])

@router.post("/register", response_model=UserResponse, status_code=201)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    new_user = await handlers.create_user(user.username, user.email, user.password, db)
    return new_user

@router.post("/login", response_model=Token)
async def login(user: UserCreate, db: AsyncSession = Depends(get_db)):
    valid_user = await handlers.authenticate_user(user.email, user.password, db)
    token_data = {"sub": str(valid_user.email)}
    return {
        "access_token": jwt.create_access_token(token_data),
        "refresh_token": jwt.create_refresh_token(token_data),
    }

@router.post("/refresh", response_model=Token)
async def refresh_token(request: Request, db: AsyncSession = Depends(get_db)):
    redis = await get_redis()

    rt = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="No refresh token")

    try:
        payload = jwt.decode_token(refresh_token)
        email = payload.get("sub")
        stored_token = await redis.get(f"refresh_token:{email}")
        if stored_token != refresh_token:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    token_data = {"sub": email}
    access_token = jwt.create_access_token(token_data)
    new_refresh_token = jwt.create_refresh_token(token_data)

    await redis.set(f"refresh_token:{email}", new_refresh_token)

    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token
    }

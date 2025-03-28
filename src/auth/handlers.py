from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.database.db import get_db
from src.database.models import User
from src.auth.hashing import hash_password, verify_password
from src.auth.jwt import create_access_token, create_refresh_token, decode_token

async def create_user(username: str, email: str, password: str, db: AsyncSession):
    stmt = select(User).where(User.email == email)
    result = await db.execute(stmt)
    if result.scalar():
        raise HTTPException(status_code=409, detail="Email already registered")
    user = User(username=username, email=email, password=hash_password(password))
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

async def authenticate_user(email: str, password: str, db: AsyncSession):
    stmt = select(User).where(User.email == email)
    result = await db.execute(stmt)
    user = result.scalar()
    if not user or not verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return user

async def get_current_user(token: str = Depends(...), db: AsyncSession = Depends(get_db)):
    try:
        payload = decode_token(token)
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        stmt = select(User).where(User.email == email)
        result = await db.execute(stmt)
        return result.scalar()
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

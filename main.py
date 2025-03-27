from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.api.contacts import router as contacts_router
from src.database.db import engine
from src.database.models import Base

@asynccontextmanager
async def lifespan(_: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(contacts_router)

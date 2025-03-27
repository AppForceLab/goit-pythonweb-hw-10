from fastapi import APIRouter, Depends, HTTPException, Query, status, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from src.database.db import get_db
from src.schemas.contacts import ContactCreate, ContactResponse, ContactUpdate
from src.repository import contacts as repo_contacts
from typing import List, Optional

router = APIRouter(prefix="/api/v1/contacts", tags=["contacts"])


@router.post("/", response_model=ContactResponse)
async def create(contact: ContactCreate, db: AsyncSession = Depends(get_db)):
    return await repo_contacts.create_contact(contact, db)


@router.get("/", response_model=List[ContactResponse])
async def read_contacts(
    skip: int = 0,
    limit: int = 10,
    search: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    return await repo_contacts.get_contacts(skip, limit, search, db)


@router.get("/birthdays", response_model=List[ContactResponse])
async def upcoming_birthdays(db: AsyncSession = Depends(get_db)):
    return await repo_contacts.get_upcoming_birthdays(db)


@router.get("/{contact_id}", response_model=ContactResponse)
async def read_contact(
    contact_id: int = Path(ge=1), db: AsyncSession = Depends(get_db)
):
    contact = await repo_contacts.get_contact(contact_id, db)
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact


@router.put("/{contact_id}", response_model=ContactResponse)
async def update(
    contact_id: int, contact: ContactUpdate, db: AsyncSession = Depends(get_db)
):
    updated_contact = await repo_contacts.update_contact(contact_id, contact, db)
    if not updated_contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return updated_contact


@router.delete("/{contact_id}")
async def delete(contact_id: int, db: AsyncSession = Depends(get_db)):
    deleted_contact = await repo_contacts.delete_contact(contact_id, db)
    if not deleted_contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return {"message": "Deleted successfully"}


@router.get("/healthcheck")
async def healthcheck(db: AsyncSession = Depends(get_db)):
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "OK"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )

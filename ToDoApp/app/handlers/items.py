import uuid
import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.engine import Item
from app.models.items import (
    ItemListResponse,
    ItemCreateRequest,
    ItemUpdateRequest,
    ItemResponse,
)
from app.utils.utils import get_db


router = APIRouter(prefix="/items", tags=["items"])


@router.post("/")
async def create_item(
    item: ItemCreateRequest, db: Session = Depends(get_db)
) -> ItemResponse:
    new_item = Item(**item.dict())
    new_item.id = uuid.uuid4()
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item


@router.get("/")
async def get_items(db: Session = Depends(get_db)) -> ItemListResponse:
    items = db.query(Item).all()
    return {"items": items}


@router.get("/{item_id}")
async def get_item(item_id: uuid.UUID, db: Session = Depends(get_db)) -> ItemResponse:
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.put("/{item_id}")
async def update_item(
    item_id: uuid.UUID, item_update: ItemUpdateRequest, db: Session = Depends(get_db)
) -> ItemResponse:
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    for key, value in item_update.dict(exclude_unset=True).items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}")
async def delete_item(item_id: uuid.UUID, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(item)
    db.commit()
    return item

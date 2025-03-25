import uuid
import datetime
from typing import List, Optional

from pydantic import BaseModel


class ItemCreateRequest(BaseModel):
    title: str
    description: str
    todo: datetime.datetime
    done: bool | None = False


class ItemUpdateRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    todo: Optional[datetime.datetime] = None
    done: Optional[bool] | None = False


class ItemResponse(BaseModel):
    id: uuid.UUID
    title: str
    description: str
    todo: datetime.datetime
    done: bool
    created_at: datetime.datetime
    updated_at: datetime.datetime


class ItemListResponse(BaseModel):
    items: List[ItemResponse]

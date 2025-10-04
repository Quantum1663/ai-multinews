from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import List
from ..db import list_articles

router = APIRouter(prefix="/feed", tags=["feed"])

class FeedItem(BaseModel):
    id: str
    title: str
    source: str | None = None
    m: float
    h: float
    cred: float
    agree: float
    created_at: str

class FeedOut(BaseModel):
    items: List[FeedItem]

@router.get("", response_model=FeedOut)
def feed(limit: int = Query(20, ge=1, le=100), offset: int = Query(0, ge=0)):
    items = list_articles(limit=limit, offset=offset)
    return {"items": items}

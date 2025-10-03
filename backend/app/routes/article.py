from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..utils.store import get_article

router = APIRouter(prefix="/article", tags=["article"])

class ArticleOut(BaseModel):
    id: str
    title: str
    source: str | None = None
    url: str | None = None
    text: str

@router.get("/{aid}", response_model=ArticleOut)
def read_article(aid: str):
    art = get_article(aid)
    if not art:
        raise HTTPException(status_code=404, detail="Article not found")
    return art

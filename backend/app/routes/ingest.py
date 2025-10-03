from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import requests
from bs4 import BeautifulSoup
from ..utils.store import create_article

router = APIRouter(prefix="/ingest", tags=["ingest"])

class IngestIn(BaseModel):
    url: Optional[str] = None
    text: Optional[str] = None
    img_url: Optional[str] = None
    lang: Optional[str] = "auto"

@router.post("")
def ingest(payload: IngestIn):
    if payload.url:
        try:
            r = requests.get(payload.url, timeout=15)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, "html.parser")
            title = (soup.title.string.strip() if soup.title and soup.title.string else payload.url)
            paras = [p.get_text(" ", strip=True) for p in soup.find_all("p")]
            text = " ".join(paras).strip()
            text = text[:8000]  # keep response light
            aid = create_article(title=title, text=text, url=payload.url)
            return {"ok": True, "id": aid}
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to fetch URL: {e}")
    if payload.text:
        aid = create_article(title="Pasted text", text=payload.text, url=None)
        return {"ok": True, "id": aid}
    raise HTTPException(status_code=400, detail="Provide url or text")


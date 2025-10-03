from typing import Dict, Optional
from uuid import uuid4
from .credibility import domain_from_url

STORE: Dict[str, dict] = {}  # in-memory store for demo

def create_article(title: str, text: str, url: Optional[str] = None) -> str:
    aid = uuid4().hex[:8]
    STORE[aid] = {
        "id": aid,
        "title": title or "Untitled",
        "url": url,
        "source": (domain_from_url(url) if url else "Custom"),
        "text": text or "",
    }
    return aid

def get_article(aid: str) -> Optional[dict]:
    return STORE.get(aid)

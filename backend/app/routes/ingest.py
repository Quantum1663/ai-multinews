from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import requests, uuid
from bs4 import BeautifulSoup
from ..utils.credibility import credibility, domain_from_url
from ..models.loader import get_model
from ..utils.verify import agreement_and_refs
from ..db import upsert_article, get_by_url

router = APIRouter(prefix="/ingest", tags=["ingest"])

class IngestIn(BaseModel):
    url: Optional[str] = None
    text: Optional[str] = None
    lang: Optional[str] = "auto"

def _extract(url: str) -> tuple[str, str]:
    r = requests.get(url, timeout=15)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    title = (soup.title.string.strip() if soup.title and soup.title.string else url)
    paras = [p.get_text(" ", strip=True) for p in soup.find_all("p")]
    text = " ".join(paras).strip()
    return title, text

@router.post("")
def ingest(payload: IngestIn):
    if not (payload.url or payload.text):
        raise HTTPException(status_code=400, detail="Provide url or text")

    url = payload.url
    # If URL already ingested, return the existing id
    if url:
        existing = get_by_url(url)
        if existing:
            return {"ok": True, "id": existing["id"]}

    try:
        if url:
            title, text = _extract(url)
            if not text:
                raise ValueError("No article text extracted")
            source = domain_from_url(url)
        else:
            title = "Pasted text"
            text = payload.text or ""
            source = "Custom"
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch/parse: {e}")

    # Compute scores now (for Feed)
    cls = get_model().infer(text, payload.lang)
    cred = credibility(url).score
    agree, _refs = agreement_and_refs(text)

    aid = uuid.uuid4().hex[:8]
    upsert_article(
        aid=aid, title=title[:300], text=text[:8000], url=url, source=source,
        misinfo=float(cls.misinfo_prob), hate=float(cls.hate_prob),
        cred=float(cred), agree=float(agree)
    )
    return {"ok": True, "id": aid}


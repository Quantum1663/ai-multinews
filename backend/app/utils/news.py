import os
import requests
from typing import List, Dict

NEWSAPI_KEY = os.environ.get("NEWSAPI_KEY")

WHITELIST = {
    "bbc.co.uk", "bbc.com", "thehindu.com", "indianexpress.com", "ndtv.com",
    "pib.gov.in", "reuters.com", "apnews.com", "theguardian.com",
}

def search_news(query: str, lang: str = "en", page_size: int = 10) -> List[Dict]:
    if not NEWSAPI_KEY:
        return []
    # Use English search for now; NewsAPI supports many langs
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": query[:256], "pageSize": page_size, "sortBy": "relevancy", "language": "en"
    }
    headers = {"X-Api-Key": NEWSAPI_KEY}
    r = requests.get(url, params=params, headers=headers, timeout=15)
    r.raise_for_status()
    items = r.json().get("articles", [])[:page_size]
    out = []
    for a in items:
        src = (a.get("source") or {}).get("name") or ""
        domain = (a.get("url") or "").split("/")[2].replace("www.", "")
        # light whitelist boost: leave non-whitelist too (we’ll filter by similarity later)
        out.append({
            "title": a.get("title") or "",
            "description": a.get("description") or "",
            "url": a.get("url") or "",
            "source": src,
            "domain": domain,
            "is_trusted": domain in WHITELIST
        })
    return out

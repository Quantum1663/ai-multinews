from urllib.parse import urlparse
from dataclasses import dataclass

WHITELIST = {"pib.gov.in":0.98,"thehindu.com":0.92,"indianexpress.com":0.90,"bbc.com":0.90,"ndtv.com":0.85}

@dataclass
class CredResult:
    domain:str; score:float

def domain_from_url(url: str) -> str|None:
    try:
        return urlparse(url).netloc.replace("www.","")
    except Exception:
        return None

def credibility(url: str|None) -> CredResult:
    if not url: return CredResult(domain="", score=0.6)  # neutral prior
    dom = domain_from_url(url) or ""
    base = 0.6
    if dom in WHITELIST: base = WHITELIST[dom]
    return CredResult(domain=dom, score=base)

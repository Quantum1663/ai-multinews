import re
import unicodedata

URL_RE = re.compile(r"https?://\S+")
EMOJI_RE = re.compile(r"[\U00010000-\U0010ffff]", flags=re.UNICODE)

def normalize(text: str) -> str:
    t = unicodedata.normalize("NFKC", text or "")
    t = t.lower().strip()
    t = URL_RE.sub(" ", t)
    t = EMOJI_RE.sub(" ", t)
    t = re.sub(r"\s+", " ", t)
    return t

# tiny roman->devanagari demo map (extend later)
ROMAN2HIN = {"nahi":"नहीं","kya":"क्या","hai":"है","tha":"था"}

def code_mix_normalize(text: str) -> str:
    words = text.split()
    out = []
    for w in words:
        out.append(ROMAN2HIN.get(w, w))
    return " ".join(out)

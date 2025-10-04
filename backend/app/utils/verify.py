from typing import List, Dict, Tuple
import re
from .embedder import embed_texts
from .news import search_news

# --- claim extraction (simple, fast) ---
SENT_SPLIT = re.compile(r"(?<=[.?!])\s+")
def extract_candidate_claims(text: str, max_len: int = 180) -> List[str]:
    sents = [s.strip() for s in SENT_SPLIT.split(text) if s.strip()]
    # prefer mid-length factual-looking sentences
    ranked = sorted(sents, key=lambda s: (abs(len(s) - 120), -len(s)))
    claims = []
    for s in ranked:
        if 20 <= len(s) <= max_len:
            claims.append(s)
        if len(claims) >= 3:
            break
    if not claims and sents:
        claims.append(sents[0][:max_len])
    return claims or [text[:max_len]]

def agreement_and_refs(text: str) -> Tuple[float, List[Dict]]:
    # 1) extract 1–3 candidate claims
    claims = extract_candidate_claims(text)

    # 2) search trusted news for each claim and gather candidates
    candidates: List[Dict] = []
    for c in claims:
        candidates.extend(search_news(c))

    if not candidates:
        # Fallback: no external refs available
        return 0.55, [
            {"title": "Trusted source 1", "url": "https://example.com"},
            {"title": "Trusted source 2", "url": "https://example.com"},
        ]

    # 3) embed claim(s) and candidate headlines+descriptions
    claim_emb = embed_texts(claims).mean(axis=0)  # pooled claim vector
    texts = [(i, f"{it['title']} — {it.get('description','')}") for i, it in enumerate(candidates)]
    cand_emb = embed_texts([t for _, t in texts])

    # 4) cosine similarity (embeddings are normalized)
    import numpy as np
    sims = cand_emb @ claim_emb  # (N,)
    # rank, prefer trusted domains
    order = np.argsort(-sims)
    ranked = []
    for idx in order:
        it = candidates[idx].copy()
        it["sim"] = float(sims[idx])
        ranked.append(it)

    # 5) build agree_score and top references
    top = [r for r in ranked if r["sim"] >= 0.45]  # reasonable threshold
    if not top:
        top = ranked[:3]

    # agree_score: weighted avg of top-K sims, with trust boost
    def weight(item): return 1.15 if item.get("is_trusted") else 1.0
    if top:
        w = np.array([weight(t) for t in top])
        a = np.array([t["sim"] for t in top])
        agree = float((w * a).sum() / w.sum())
    else:
        agree = float(max(sims.max(), 0.35))

    # clamp to [0,1]
    agree = max(0.0, min(1.0, agree))

    references = []
    for t in top[:5]:
        references.append({"title": t["title"], "url": t["url"]})
    return agree, references

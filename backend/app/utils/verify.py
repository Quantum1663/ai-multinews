from typing import List, Dict

# Placeholder: in real code, embed text & compare with trusted corpora.
def agreement_score(text: str) -> float:
    # Very naive heuristic for now: longer, factual-looking text -> higher
    length = min(len(text)/600, 1.0)
    return 0.5 + 0.4*length

def references_stub(text: str) -> List[Dict]:
    return [
        {"title": "Trusted source 1", "url": "https://example.com"},
        {"title": "Trusted source 2", "url": "https://example.com"}
    ]

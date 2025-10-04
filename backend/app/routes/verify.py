from fastapi import APIRouter
from pydantic import BaseModel
from ..utils.credibility import credibility
from ..utils.verify import agreement_and_refs

router = APIRouter(prefix="/verify", tags=["verify"])

class VerifyIn(BaseModel):
    text: str
    url: str | None = None

class Reference(BaseModel):
    title: str
    url: str

class VerifyOut(BaseModel):
    cred_score: float
    agree_score: float
    references: list[Reference]

@router.post("", response_model=VerifyOut)
def verify(payload: VerifyIn):
    cred = credibility(payload.url)
    agree, refs = agreement_and_refs(payload.text)
    return VerifyOut(
        cred_score=round(cred.score, 2),
        agree_score=round(agree, 2),
        references=[Reference(**r) for r in refs]
    )

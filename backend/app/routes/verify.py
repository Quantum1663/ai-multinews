from fastapi import APIRouter
from pydantic import BaseModel
from ..utils.credibility import credibility
from ..utils.verify import agreement_score, references_stub

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
    agree = agreement_score(payload.text)
    refs = [Reference(**r) for r in references_stub(payload.text)]
    return VerifyOut(cred_score=round(cred.score, 2), agree_score=round(agree, 2), references=refs)

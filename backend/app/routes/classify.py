from fastapi import APIRouter
from pydantic import BaseModel
from ..models.loader import get_model

router = APIRouter(prefix="/classify", tags=["classify"])

class ClassifyIn(BaseModel):
    text: str
    lang: str | None = "auto"

class ClassifyOut(BaseModel):
    hate_prob: float
    misinfo_prob: float
    spans: list

@router.post("", response_model=ClassifyOut)
def classify(payload: ClassifyIn):
    m = get_model().infer(payload.text, payload.lang)
    return ClassifyOut(hate_prob=m.hate_prob, misinfo_prob=m.misinfo_prob, spans=m.spans)

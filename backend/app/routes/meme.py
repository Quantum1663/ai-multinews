from fastapi import APIRouter, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/meme-check", tags=["meme"])

class MemeOut(BaseModel):
    clip_delta: float
    heatmap: Optional[str] = None

@router.post("", response_model=MemeOut)
async def meme_check(img: UploadFile = File(...), caption: str | None = Form(None)):
    # TODO: run CLIP; return heatmap as data URL if you generate one
    # For now, pretend a small mismatch if caption present
    delta = 0.12 if caption else 0.04
    return MemeOut(clip_delta=delta)

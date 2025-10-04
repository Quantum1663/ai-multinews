from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from typing import Optional
from functools import lru_cache
from io import BytesIO
import torch
from contextlib import nullcontext
from PIL import Image
from transformers import CLIPModel, CLIPProcessor

router = APIRouter(prefix="/meme-check", tags=["meme"])

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

@lru_cache(maxsize=1)
def get_clip():
    model_name = "openai/clip-vit-base-patch32"
    model = CLIPModel.from_pretrained(model_name).to(DEVICE)
    processor = CLIPProcessor.from_pretrained(model_name)
    model.eval()
    return model, processor

class MemeOut(BaseModel):
    clip_delta: float
    heatmap: Optional[str] = None

def cosine_sim(img_feat: torch.Tensor, txt_feat: torch.Tensor) -> float:
    img_feat = torch.nn.functional.normalize(img_feat, dim=-1)
    txt_feat = torch.nn.functional.normalize(txt_feat, dim=-1)
    return float((img_feat @ txt_feat.T).squeeze().item())

@router.post("", response_model=MemeOut)
async def meme_check(img: UploadFile = File(...), caption: str | None = Form(None)):
    try:
        raw = await img.read()
        pil = Image.open(BytesIO(raw)).convert("RGB")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid image")

    text = caption.strip() if caption else "a generic meme"

    model, processor = get_clip()

    # autocast on CUDA for speed
    amp = torch.autocast(device_type="cuda", dtype=torch.float16) if DEVICE.type == "cuda" else nullcontext()

    with torch.inference_mode(), amp:
        inputs_img = processor(images=pil, return_tensors="pt")
        inputs_txt = processor.tokenizer([text], return_tensors="pt", padding=True, truncation=True)

        inputs_img = {k: v.to(DEVICE) for k, v in inputs_img.items()}
        inputs_txt = {k: v.to(DEVICE) for k, v in inputs_txt.items()}

        img_feat = model.get_image_features(**inputs_img)   # (1, 512)
        txt_feat = model.get_text_features(**inputs_txt)    # (1, 512)

        sim = cosine_sim(img_feat, txt_feat)
        threshold = 0.30
        clip_delta = max(0.0, threshold - sim)

    return MemeOut(clip_delta=round(clip_delta, 3), heatmap=None)

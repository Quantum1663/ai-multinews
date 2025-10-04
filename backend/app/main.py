from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes.classify import router as classify_router
from .routes.verify import router as verify_router
from .routes.ingest import router as ingest_router
from .routes.meme import router as meme_router
from .routes.article import router as article_router
from .routes.feed import router as feed_router
from .db import init_db
from .models.loader import get_model
try:
    from .routes.meme import get_clip
except Exception:
    get_clip = None

app = FastAPI(title="AI Multilingual News API", version="0.2.0")

origins = ["http://localhost:5173", "http://127.0.0.1:5173"]
app.add_middleware(
    CORSMiddleware, allow_origins=origins, allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

@app.on_event("startup")
def _startup():
    init_db()
    get_model()
    if get_clip:
        try: get_clip()
        except Exception: pass

@app.get("/")
def root():
    return {"ok": True, "service": "ai-multinews-api"}

app.include_router(classify_router)
app.include_router(verify_router)
app.include_router(ingest_router)
app.include_router(article_router)
app.include_router(meme_router)
app.include_router(feed_router)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes.classify import router as classify_router
from .routes.verify import router as verify_router
from .routes.ingest import router as ingest_router
from .routes.meme import router as meme_router
from .routes.article import router as article_router
app = FastAPI(title="AI Multilingual News API", version="0.1.0")
app.include_router(article_router)
origins = ["http://localhost:5173", "http://127.0.0.1:5173"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

@app.get("/")
def root():
    return {"ok": True, "service": "ai-multinews-api"}

app.include_router(classify_router)
app.include_router(verify_router)
app.include_router(ingest_router)
app.include_router(meme_router)

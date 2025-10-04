from functools import lru_cache
from sentence_transformers import SentenceTransformer

@lru_cache(maxsize=1)
def get_embedder():
    # Multilingual, small & fast; good for EN/HI/UR
    return SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

def embed_texts(texts: list[str]):
    model = get_embedder()
    return model.encode(texts, normalize_embeddings=True)

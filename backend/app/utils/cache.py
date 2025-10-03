from functools import lru_cache

@lru_cache(maxsize=2048)
def memo(key: str, value=None):
    # Use as: v = memo(url) or memo(url, value) to set
    return value

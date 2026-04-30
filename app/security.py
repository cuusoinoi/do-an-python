import hashlib


def md5_hash(raw: str) -> str:
    return hashlib.md5(raw.encode("utf-8")).hexdigest()

import hashlib


def generate_hash(s: str) -> str:
    hasher = hashlib.sha256()
    # Encode the string to bytes
    hasher.update(s.encode("utf-8"))
    return hasher.hexdigest()

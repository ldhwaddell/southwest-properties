import hashlib
import re


def generate_hash(s: str) -> str:
    hasher = hashlib.sha256()
    # Encode the string to bytes
    hasher.update(s.encode("utf-8"))
    return hasher.hexdigest()


def clean_whitespace(text: str) -> str:
    """Replace one or more whitespace characters (including non-breaking spaces) with a single space"""
    if text is not None:
        return re.sub(r"\s+", " ", text)

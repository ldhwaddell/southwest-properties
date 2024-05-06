import hashlib
import re

from airflow.providers.redis.hooks.redis import RedisHook


def generate_hash(s: str) -> str:
    hasher = hashlib.sha256()
    # Encode the string to bytes
    hasher.update(s.encode("utf-8"))
    return hasher.hexdigest()


def clean_whitespace(text: str) -> str:
    """Replace one or more whitespace characters (including non-breaking spaces) with a single space"""
    if text is not None:
        return re.sub(r"\s+", " ", text)


def load_from_redis(conn_id: str, key: str) -> bytes:
    redis_hook = RedisHook(redis_conn_id=conn_id).get_conn()

    with redis_hook.pipeline() as pipe:
        pipe.get(key)
        pipe.delete(key)
        result = pipe.execute()

    # [0] is get, [1] is delete status
    value = result[0]

    if value is None:
        raise ValueError(f"No data found in Redis for key: {key}")

    return value

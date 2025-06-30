import redis
import json
import os

class RedisCache:
    def __init__(self, host='localhost', port=6379, db=0, prefix='kaggle-agent:cache'):
        self.client = redis.Redis(host=host, port=port, db=db)
        self.prefix = prefix

    def _make_key(self, section: str, content_hash: str) -> str:
        return f"{self.prefix}:{section}:{content_hash}"

    def get_cache(self, section: str, content_hash: str):
        key = self._make_key(section, content_hash)
        value = self.client.get(key)
        if value:
            return json.loads(value)
        return None

    def update_cache(self, section: str, content_hash: str, deep_scraped: bool):
        key = self._make_key(section, content_hash)
        value = json.dumps({"deep_scraped": deep_scraped})
        self.client.set(key, value)

    def is_scraped(self, section: str, content_hash: str) -> bool:
        data = self.get_cache(section, content_hash)
        return data is not None and data.get("deep_scraped", False)

    def flush_cache(self):
        pattern = f"{self.prefix}:*"
        for key in self.client.scan_iter(match=pattern):
            self.client.delete(key)

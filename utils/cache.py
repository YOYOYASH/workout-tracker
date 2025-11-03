from redis import Redis
from redis.exceptions import ConnectionError
from config import Config

class Cache:
    def __init__(self, host='localhost', port=6379, db=0):
        # self.redis = Redis(host=host, port=port, db=db, decode_responses=True)
        self.redis = Redis.from_url(f"rediss://default:{Config.REDIS_PASSWORD}@organic-guppy-35039.upstash.io:6379", decode_responses=True)
        self.key = {}
        try:
            self.redis.ping()
        except ConnectionError:
            raise ConnectionError("Could not connect to Redis server")

    def set(self, key, value, ex=None):
        """Set a value in the cache with an optional expiration time."""
        self.redis.set(key, value, ex=ex)

    def get(self, key):
        """Get a value from the cache."""
        return self.redis.get(key)

    def delete(self, key):
        """Delete a key from the cache."""
        self.redis.delete(key)
        print(f"Cache key '{key}' deleted.")

    def exists(self, key):
        """Check if a key exists in the cache."""
        return self.redis.exists(key)

    def clear(self):
        """Clear the entire cache."""
        self.redis.flushdb()


cache = Cache()  # Create a global cache instance
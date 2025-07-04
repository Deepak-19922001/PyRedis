import threading
import time
from collections import deque

class PyRedisDB:
    def __init__(self):
        self._data = {}
        self._expirations = {}
        self._lock = threading.Lock()

    def _is_expired(self, key):
        if key in self._expirations and self._expirations[key] < time.time():
            if key in self._data:
                del self._data[key]
            del self._expirations[key]
            return True
        return False

    def get(self, key):
        with self._lock:
            if self._is_expired(key):
                return None
            value = self._data.get(key)
            return value if isinstance(value, str) else None

    def set(self, key, value, expiry_seconds=None):
        with self._lock:
            self._data[key] = str(value)
            if expiry_seconds:
                self._expirations[key] = time.time() + expiry_seconds
            elif key in self._expirations:
                del self._expirations[key]
            return "OK"

    def delete(self, keys):
        with self._lock:
            deleted_count = 0
            for k in keys:
                if self._is_expired(k):
                    continue
                if k in self._data:
                    del self._data[k]
                    if k in self._expirations:
                        del self._expirations[k]
                    deleted_count += 1
            return deleted_count


    def hset(self, key, field, value):
        with self._lock:
            self._is_expired(key)
            if key not in self._data or not isinstance(self._data.get(key), dict):
                self._data[key] = {}
            self._data[key][field] = value
            return 1

    def hget(self, key, field):
        with self._lock:
            if self._is_expired(key):
                return None
            hash_map = self._data.get(key)
            return hash_map.get(field) if isinstance(hash_map, dict) else None

    def lpush(self, key, *values):
        with self._lock:
            self._is_expired(key)
            if key not in self._data or not isinstance(self._data.get(key), deque):
                self._data[key] = deque()
            for value in reversed(values):
                self._data[key].appendleft(value)
            return len(self._data[key])

    def rpush(self, key, *values):
        with self._lock:
            self._is_expired(key)
            if key not in self._data or not isinstance(self._data.get(key), deque):
                self._data[key] = deque()
            self._data[key].extend(values)
            return len(self._data[key])

    def lpop(self, key):
        with self._lock:
            if self._is_expired(key):
                return None
            lst = self._data.get(key)
            return lst.popleft() if isinstance(lst, deque) and lst else None

    def rpop(self, key):
        with self._lock:
            if self._is_expired(key):
                return None
            lst = self._data.get(key)
            return lst.pop() if isinstance(lst, deque) and lst else None

    def lrange(self, key, start, end):
        with self._lock:
            if self._is_expired(key):
                return []
            lst = self._data.get(key)
            if not isinstance(lst, deque):
                return []
            if end < 0:
                end_index = end + 1
                if end_index == 0:
                    return list(lst)[start:]
                else:
                    return list(lst)[start:end_index]
            else:
                return list(lst)[start:end + 1]

    def rrange(self, key, start, end):
        with self._lock:
            result = self.lrange(key, start, end)
            result.reverse()
            return result




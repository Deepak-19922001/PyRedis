import threading
import time
from collections import deque
import fnmatch


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

    def exists(self, keys):
        with self._lock:
            count = 0
            for key in keys:
                if not self._is_expired(key) and key in self._data:
                    count += 1
            return count

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

    def keys(self, pattern):
        with self._lock:
            all_keys = list(self._data.keys())
            for key in all_keys:
                self._is_expired(key)
            return [key for key in self._data.keys() if fnmatch.fnmatch(key, pattern)]

    def flushdb(self):
        with self._lock:
            self._data.clear()
            self._expirations.clear()
            return "OK"

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

    def incr_decr(self, key, increment):
        with self._lock:
            if self._is_expired(key):
                self._data[key] = str(increment)
                return increment

            value = self._data.get(key, '0')
            try:
                new_value = int(value) + increment
                self._data[key] = str(new_value)
                return new_value
            except (ValueError, TypeError):
                return "ERR value is not an integer or out of range"

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

            if end == -1:
                return list(lst)[start:]
            else:
                return list(lst)[start:end + 1]

    def rrange(self, key, start, end):
        with self._lock:
            result = self.lrange(key, start, end)
            result.reverse()
            return result
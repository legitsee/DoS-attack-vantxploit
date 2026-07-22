import threading
from itertools import cycle

class ProxyRotator:
    def __init__(self, filepath="proxies.txt"):
        self._proxies = []
        self._cycle = None
        self._lock = threading.Lock()
        self._load(filepath)

    def _load(self, filepath):
        try:
            with open(filepath) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        self._proxies.append(line)
        except FileNotFoundError:
            pass
        if self._proxies:
            self._cycle = cycle(self._proxies)

    def get_proxy(self):
        if not self._cycle:
            return None
        with self._lock:
            raw = next(self._cycle)
        if "@" in raw:
            return {"http": f"http://{raw}", "https": f"http://{raw}"}
        return {"http": f"http://{raw}", "https": f"http://{raw}"}

    @property
    def count(self):
        return len(self._proxies)

    @property
    def available(self):
        return self.count > 0

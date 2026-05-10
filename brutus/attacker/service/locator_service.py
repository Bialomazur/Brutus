import ipaddress
import json
import socket
import threading
import time
from pathlib import Path

from brutus.attacker.service.service import Service

_CACHE_FILE = Path(__file__).parent / "locator_cache.json"
_WHOIS_HOST = "whois.cymru.com"
_WHOIS_PORT = 43
_CACHE_TTL = 60 * 60 * 24 * 7  # 7 days
_CACHE_LOCK = threading.Lock()


class LocatorService(Service):
    """Resolve a human-readable location for an IP address (no listening socket)."""

    def __init__(
        self,
        cache_file: Path = _CACHE_FILE,
        whois_host: str = _WHOIS_HOST,
        whois_port: int = _WHOIS_PORT,
        cache_ttl: int = _CACHE_TTL,
    ) -> None:
        super().__init__("127.0.0.1", 0)
        self.cache_file = cache_file
        self.whois_host = whois_host
        self.whois_port = whois_port
        self.cache_ttl = cache_ttl

    def run(self) -> None:
        pass

    def _load_cache(self) -> dict:
        try:
            with _CACHE_LOCK, open(self.cache_file, encoding="utf-8") as fh:
                return json.load(fh)
        except Exception:
            return {}

    def _save_cache(self, cache: dict) -> None:
        try:
            with _CACHE_LOCK, open(self.cache_file, "w", encoding="utf-8") as fh:
                json.dump(cache, fh, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def _whois_lookup(self, ip: str) -> dict | None:
        try:
            with socket.create_connection((self.whois_host, self.whois_port), timeout=5) as s:
                s.sendall(f" -v {ip}\r\n".encode())
                resp = b""
                while chunk := s.recv(4096):
                    resp += chunk
                decoded = resp.decode(errors="ignore").splitlines()
                lines = [ln.strip() for ln in decoded if ln.strip()]
                if len(lines) >= 2:
                    parts = [p.strip() for p in lines[-1].split("|")]
                    if len(parts) >= 4:
                        return {"asn": parts[0], "cc": parts[3], "as_name": parts[-1]}
        except Exception:
            pass
        return None

    def get_location(self, ip: str) -> str:
        try:
            if ipaddress.ip_address(ip).is_private:
                return "   Localhost"
        except Exception:
            return ""

        cache = self._load_cache()
        entry = cache.get(ip)
        now = int(time.time())
        if entry and (now - entry.get("ts", 0) < self.cache_ttl):
            return entry.get("location", "")

        hostname = None
        try:
            hostname = socket.gethostbyaddr(ip)[0]
        except Exception:
            pass

        whois = self._whois_lookup(ip)
        parts = []
        if whois:
            parts.append(whois["cc"])
        if hostname:
            parts.append(hostname)
        elif whois:
            parts.append(whois["as_name"])
        else:
            parts.append(ip)

        location = "   " + " , ".join(parts)
        cache[ip] = {"ts": now, "location": location}
        self._save_cache(cache)
        return location


# Module-level singleton for convenience
locator = LocatorService()

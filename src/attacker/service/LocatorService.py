from src.attacker.service.Service import Service
import socket
import os
import json
import ipaddress
import time
import threading

HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Max-Age': '3600',
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
}

CACHE_FILE = os.path.join(os.path.dirname(__file__), "locator_cache.json")
WHOIS_HOST = "whois.cymru.com"
WHOIS_PORT = 43
CACHE_TTL = 60 * 60 * 24 * 7  # 7 days
_CACHE_LOCK = threading.Lock()


class LocatorService(Service):
    """Service-like helper that resolves a human-readable location for an IP address.
    Inherits Service for API consistency with other services; it does not open a listening socket by default.
    """

    def __init__(self, host: str = "127.0.0.1", port: int = 0, cache_file: str = CACHE_FILE,
                 whois_host: str = WHOIS_HOST, whois_port: int = WHOIS_PORT,
                 cache_ttl: int = CACHE_TTL):
        super().__init__(host, port)
        self.cache_file = cache_file
        self.whois_host = whois_host
        self.whois_port = whois_port
        self.cache_ttl = cache_ttl

    def _load_cache(self):
        """Load the local cache from disk; return {} if missing or invalid."""
        try:
            with _CACHE_LOCK:
                with open(self.cache_file, "r", encoding="utf-8") as fh:
                    return json.load(fh)
        except Exception:
            return {}

    def _save_cache(self, cache):
        """Persist the cache to disk."""
        try:
            with _CACHE_LOCK:
                with open(self.cache_file, "w", encoding="utf-8") as fh:
                    json.dump(cache, fh, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def _whois_cymru_lookup(self, ip: str):
        """Query Team Cymru whois service over TCP to obtain ASN and country."""
        try:
            with socket.create_connection((self.whois_host, self.whois_port), timeout=5) as s:
                query = f" -v {ip}\r\n"
                s.sendall(query.encode("utf-8"))
                resp = b""
                while True:
                    chunk = s.recv(4096)
                    if not chunk:
                        break
                    resp += chunk
                text = resp.decode("utf-8", errors="ignore")
                lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
                if len(lines) >= 2:
                    last = lines[-1]
                    parts = [p.strip() for p in last.split("|")]
                    if len(parts) >= 4:
                        asn = parts[0]
                        cc = parts[3]
                        as_name = parts[-1]
                        return {"asn": asn, "cc": cc, "as_name": as_name}
        except Exception:
            pass
        return None

    def get_location(self, ip: str) -> str:
        """Return a human-readable location string for the given IP."""
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

        # Attempt reverse DNS (hostname)
        hostname = None
        try:
            hostname = socket.gethostbyaddr(ip)[0]
        except Exception:
            hostname = None

        # Attempt whois-based lookup for country/asn
        whois_info = self._whois_cymru_lookup(ip)
        country = None
        aspart = None
        if whois_info:
            country = whois_info.get("cc")
            aspart = whois_info.get("as_name")

        parts = []
        if country:
            parts.append(country)
        if hostname:
            parts.append(hostname)
        elif aspart:
            parts.append(aspart)
        else:
            parts.append(ip)

        location = " , ".join(parts)
        location = "   " + location

        cache[ip] = {"ts": now, "location": location}
        self._save_cache(cache)
        return location


# module-level instance for compatibility with existing callers
locator = LocatorService()

def get_location(ip: str) -> str:
    """Compatibility wrapper: module-level function that forwards to the LocatorService instance."""
    return locator.get_location(ip)

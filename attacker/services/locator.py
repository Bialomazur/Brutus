from bs4 import BeautifulSoup
import requests
import socket
import os
import json
import ipaddress
import time

HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Max-Age': '3600',
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
    }


# Cache file to avoid repeated external lookups
CACHE_FILE = os.path.join(os.path.dirname(__file__), "locator_cache.json")
WHOIS_HOST = "whois.cymru.com"
WHOIS_PORT = 43
CACHE_TTL = 60 * 60 * 24 * 7  # 7 days

def _load_cache():
    """Load the local cache from disk; return {} if missing or invalid."""
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return {}

def _save_cache(cache):
    """Persist the cache to disk."""
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as fh:
            json.dump(cache, fh, ensure_ascii=False, indent=2)
    except Exception:
        pass

def _whois_cymru_lookup(ip):
    """
    Query Team Cymru whois service over TCP (port 43) to obtain ASN and country.
    This is not a REST API call; it's a plain whois TCP query.
    Returns a dict like {'asn': 'AS15169', 'cc': 'US', 'as_name': 'GOOGLE'} or None.
    """
    try:
        with socket.create_connection((WHOIS_HOST, WHOIS_PORT), timeout=5) as s:
            # Request verbose output for the single IP
            query = f" -v {ip}\r\n"
            s.sendall(query.encode("utf-8"))
            resp = b""
            while True:
                chunk = s.recv(4096)
                if not chunk:
                    break
                resp += chunk
            text = resp.decode("utf-8", errors="ignore")
            # Response has a header line; take the last non-empty data line
            lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
            if len(lines) >= 2:
                last = lines[-1]
                # Expected pipe-separated fields: AS | IP | BGP Prefix | CC | Registry | Allocated | AS Name
                parts = [p.strip() for p in last.split("|")]
                if len(parts) >= 4:
                    asn = parts[0]
                    cc = parts[3]
                    as_name = parts[-1]
                    return {"asn": asn, "cc": cc, "as_name": as_name}
    except Exception:
        pass
    return None

def get_location(ip):
    """
    Return a human-readable location string for the given IP.
    - For private IPs, return '   Localhost' (keeps previous formatting).
    - First try to return cached result.
    - Otherwise attempt reverse DNS and a whois lookup (Team Cymru) and cache the result.
    """
    try:
        if ipaddress.ip_address(ip).is_private:
            return "   Localhost"
    except Exception:
        # If ip is malformed, return an empty string to avoid crashes elsewhere.
        return ""

    cache = _load_cache()
    entry = cache.get(ip)
    now = int(time.time())
    if entry and (now - entry.get("ts", 0) < CACHE_TTL):
        return entry.get("location", "")

    # Attempt reverse DNS (hostname)
    hostname = None
    try:
        hostname = socket.gethostbyaddr(ip)[0]
    except Exception:
        hostname = None

    # Attempt whois-based lookup for country/asn
    whois_info = _whois_cymru_lookup(ip)
    country = None
    aspart = None
    if whois_info:
        country = whois_info.get("cc")
        aspart = whois_info.get("as_name")

    # Compose a readable location string: prefer "CC , hostname", else ASN/hostname, else hostname, else IP
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

    # Keep a small left padding to be visually similar to previous implementation
    location = "   " + location

    # Cache and return
    cache[ip] = {"ts": now, "location": location}
    _save_cache(cache)
    return location
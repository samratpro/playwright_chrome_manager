# proxy_config.py
import requests
from typing import Dict, Any

_country_cache = {}

def detect_country(ip: str) -> str | None:
    if ip in _country_cache:
        return _country_cache[ip]
    try:
        resp = requests.get(f"http://ip-api.com/json/{ip}?fields=countryCode", timeout=7)
        if resp.status_code == 200:
            code = resp.json().get("countryCode")
            _country_cache[ip] = code
            return code
    except:
        pass
    return None

# Add this function — detects country from DataImpulse username
def country_from_dataimpulse_username(username: str) -> str | None:
    """Extract country from username like: user__cr.fr → FR"""
    if "__cr." in username.lower():
        code = username.lower().split("__cr.")[-1].strip()
        mapping = {
            "fr": "FR", "de": "DE", "nl": "NL", "gb": "GB", "us": "US",
            "ca": "CA", "au": "AU", "jp": "JP", "it": "IT", "es": "ES",
        }
        return mapping.get(code, None)
    return None

FINGERPRINTS: Dict[str, Dict[str, Any]] = {
    "US": {"tz": "America/New_York",     "locale": "en-US", "res": (1920, 1080)},
    "GB": {"tz": "Europe/London",        "locale": "en-GB", "res": (1920, 1080)},
    "DE": {"tz": "Europe/Berlin",        "locale": "de-DE", "res": (1920, 1080)},
    "FR": {"tz": "Europe/Paris",         "locale": "fr-FR", "res": (1920, 1080)},
    "NL": {"tz": "Europe/Amsterdam",     "locale": "nl-NL", "res": (1920, 1080)},
    "CA": {"tz": "America/Toronto",      "locale": "en-CA", "res": (1920, 1080)},
    "AU": {"tz": "Australia/Sydney",     "locale": "en-AU", "res": (1920, 1080)},
    "JP": {"tz": "Asia/Tokyo",           "locale": "ja-JP", "res": (1920, 1080)},
    "IN": {"tz": "Asia/Kolkata",         "locale": "en-IN", "res": (1366, 768)},
    "BR": {"tz": "America/Sao_Paulo",    "locale": "pt-BR", "res": (1366, 768)},
    "RU": {"tz": "Europe/Moscow",        "locale": "ru-RU", "res": (1920, 1080)},
}

DEFAULT_FINGERPRINT = FINGERPRINTS["US"]
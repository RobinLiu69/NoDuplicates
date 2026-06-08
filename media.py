import re
from urllib.parse import urlparse, parse_qs

URL_PATTERN = re.compile(r'https?://\S+')

PLATFORM_NAMES = {
    "yt": "YouTube",
    "ig": "Instagram Reel",
}


def extract_media_id(url: str) -> tuple[str, str] | None:
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.replace("www.", "").lower()
        path = parsed.path

        if "youtube.com" in domain:
            if path.startswith("/watch"):
                vid = parse_qs(parsed.query).get("v", [None])[0]
                return ("yt", vid) if vid else None
            if path.startswith(("/shorts/", "/live/")):
                return "yt", path.split("/")[2]
        elif "youtu.be" in domain:
            vid = path.lstrip("/")
            return ("yt", vid) if vid else None

        if "instagram.com" in domain:
            if "/reels/" in path or "/reel/" in path:
                parts = path.split("/")
                idx = parts.index("reels") if "reels" in parts else parts.index("reel")
                if len(parts) > idx + 1 and parts[idx + 1]:
                    return "ig", parts[idx + 1]
    except Exception:
        pass
    return None


def extract_all(content: str) -> list[tuple[str, str]]:
    results = []
    seen = set()
    for url in URL_PATTERN.findall(content):
        info = extract_media_id(url)
        if info and info not in seen:
            seen.add(info)
            results.append(info)
    return results


def platform_name(media_type: str) -> str:
    return PLATFORM_NAMES.get(media_type, media_type)

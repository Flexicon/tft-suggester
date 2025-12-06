import requests_cache


CDRAGON_CDN = "https://raw.communitydragon.org/latest"
BASE_URL = f"{CDRAGON_CDN}/plugins/rcp-be-lol-game-data/global/default"


def cached_session():
    return requests_cache.CachedSession("cdragon_cache", expire_after=3600)


def asset_url(path: str) -> str:
    """Return a full URL pointing to the asset identified by the given path.

    Automatically converts .tex texture file links to .png for web compatibility.
    """
    cleaned_path = path.lower().removeprefix("/lol-game-data/assets/").removeprefix("/")
    # Convert texture file links to PNG
    if cleaned_path.endswith(".tex"):
        cleaned_path = cleaned_path[:-4] + ".png"
    return f"{BASE_URL}/{cleaned_path}"

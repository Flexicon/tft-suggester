import requests_cache


BASE_URL = "https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default"


def cached_session():
    return requests_cache.CachedSession('cdragon_cache', expire_after=3600)


def asset_url(path: str) -> str:
    """Return a full URL pointing to the asset identified by the given path."""
    return f"{BASE_URL}/{path.lower().removeprefix('/lol-game-data/assets/').removeprefix('/')}"

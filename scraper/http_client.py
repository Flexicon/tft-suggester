import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

DEFAULT_TIMEOUT = (5, 15)
RETRY_STATUS_CODES = (429, 500, 502, 503, 504)


def _build_session() -> requests.Session:
    session = requests.Session()
    retry = Retry(
        total=3,
        backoff_factor=0.5,
        status_forcelist=RETRY_STATUS_CODES,
        allowed_methods=("GET",),
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


session = _build_session()


def get(url: str, **kwargs) -> requests.Response:
    """GET a URL with timeouts and transient-error retries."""
    return session.get(url, timeout=DEFAULT_TIMEOUT, **kwargs)


def post(url: str, **kwargs) -> requests.Response:
    """POST to a URL with a timeout. POSTs are not retried."""
    return session.post(url, timeout=DEFAULT_TIMEOUT, **kwargs)

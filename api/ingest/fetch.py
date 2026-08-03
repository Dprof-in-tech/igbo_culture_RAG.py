"""Fetching and text-cleaning for corpus sources.

Everything fetched is cached on disk under ``.cache/ingest/pages`` keyed by
source, so re-running the pipeline costs no network and no politeness delay.
"""

from __future__ import annotations

import hashlib
import json
import logging
import threading
import time
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from .sources import Source

logger = logging.getLogger(__name__)

CACHE_DIR = Path(".cache/ingest/pages")
USER_AGENT = (
    "AchalugoCorpusBot/1.0 "
    "(https://github.com/Dprof-in-tech/igbo_culture_RAG.py; Igbo cultural RAG corpus)"
)
TIMEOUT = 30

# Scraped pages need a high floor, because anything short is usually surviving
# boilerplate. MediaWiki extracts are already clean, and the short ones are
# mostly Igbo name and clan stubs — dense, and worth keeping.
MIN_CHARS_WEB = 400
MIN_CHARS_WIKI = 140

# Minimum seconds between requests to one host. Wikimedia rate-limits per IP
# across all its projects, so concurrent workers must not race each other onto
# wikipedia/wikiquote at once.
HOST_INTERVAL = defaultdict(lambda: 1.0)
HOST_INTERVAL.update(
    {
        "en.wikipedia.org": 1.2,
        "ig.wikipedia.org": 1.2,
        "en.wikiquote.org": 1.2,
    }
)
RETRIES = 3

STRIP_TAGS = [
    "script",
    "style",
    "noscript",
    "nav",
    "footer",
    "header",
    "aside",
    "iframe",
    "form",
    "button",
    "figure",
    "table",
]

CONTENT_SELECTORS = [
    "article",
    "main",
    ".post-content",
    ".article-content",
    ".entry-content",
    ".post-body",
    "#content",
    ".content",
]

# Boilerplate lines that survive tag stripping on most CMS pages.
NOISE = (
    "cookie",
    "privacy policy",
    "subscribe",
    "newsletter",
    "sign up",
    "log in",
    "advertisement",
    "share this",
    "follow us",
    "all rights reserved",
    "read more",
    "related posts",
    "leave a comment",
)


@dataclass
class Page:
    key: str
    title: str
    text: str
    url: str
    tag: str
    domain: str

    def to_json(self) -> dict:
        return {
            "key": self.key,
            "title": self.title,
            "text": self.text,
            "url": self.url,
            "tag": self.tag,
            "domain": self.domain,
        }


def _cache_path(key: str) -> Path:
    digest = hashlib.sha256(key.encode("utf-8")).hexdigest()[:20]
    return CACHE_DIR / f"{digest}.json"


_session_local = threading.local()
_host_locks: dict[str, threading.Lock] = {}
_host_last: dict[str, float] = {}
_registry_lock = threading.Lock()


def _session() -> requests.Session:
    """One session per worker thread, for connection reuse."""
    session = getattr(_session_local, "session", None)
    if session is None:
        session = requests.Session()
        session.headers.update(
            {
                "User-Agent": USER_AGENT,
                "Accept-Language": "en,ig;q=0.8",
            }
        )
        _session_local.session = session
    return session


def _throttle(host: str) -> None:
    """Block until this host's minimum interval has elapsed."""
    with _registry_lock:
        lock = _host_locks.setdefault(host, threading.Lock())
    with lock:
        interval = HOST_INTERVAL[host]
        elapsed = time.monotonic() - _host_last.get(host, 0.0)
        if elapsed < interval:
            time.sleep(interval - elapsed)
        _host_last[host] = time.monotonic()


def _get(url: str, params: dict | None = None) -> requests.Response:
    """Throttled GET with backoff on rate limits and transient server errors."""
    host = urlparse(url).netloc
    last: requests.Response | None = None

    for attempt in range(RETRIES):
        _throttle(host)
        response = _session().get(url, params=params, timeout=TIMEOUT)
        if response.status_code not in (429, 502, 503, 504):
            return response

        last = response
        retry_after = response.headers.get("Retry-After")
        try:
            delay = float(retry_after) if retry_after else 0.0
        except ValueError:
            delay = 0.0
        delay = max(delay, 2.0 * (2**attempt))
        logger.info(
            "HTTP %s from %s, retrying in %.0fs (%d/%d)",
            response.status_code,
            host,
            delay,
            attempt + 1,
            RETRIES,
        )
        time.sleep(delay)

    assert last is not None
    return last


def _clean_lines(text: str) -> str:
    kept = []
    for line in text.splitlines():
        line = " ".join(line.split())
        if len(line) < 12:
            continue
        lowered = line.lower()
        if any(noise in lowered for noise in NOISE):
            continue
        kept.append(line)
    return "\n".join(kept)


def _fetch_mediawiki(source: Source) -> Page | None:
    """Plaintext article extract via the MediaWiki API."""
    api = f"https://{source.host}/w/api.php"
    params = {
        "action": "query",
        "prop": "extracts",
        "explaintext": "1",
        "redirects": "1",
        "format": "json",
        "formatversion": "2",
        "titles": source.ref,
    }
    response = _get(api, params)
    response.raise_for_status()
    pages = response.json().get("query", {}).get("pages", [])
    if not pages:
        return None

    page = pages[0]
    if page.get("missing"):
        logger.warning("Missing article: %s (%s)", source.ref, source.host)
        return None

    text = _clean_lines(page.get("extract", "") or "")
    if len(text) < MIN_CHARS_WIKI:
        logger.warning("Thin article: %s (%d chars)", source.ref, len(text))
        return None

    title = page.get("title", source.ref)
    slug = title.replace(" ", "_")
    return Page(
        key=source.key,
        title=title,
        text=text,
        url=f"https://{source.host}/wiki/{slug}",
        tag=source.tag,
        domain=source.host,
    )


def _fetch_web(source: Source) -> Page | None:
    response = _get(source.ref)
    if response.status_code != 200:
        logger.warning("HTTP %s for %s", response.status_code, source.ref)
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    for tag in soup(STRIP_TAGS):
        tag.decompose()

    title_el = soup.find("title")
    title = title_el.get_text().strip() if title_el else source.ref

    # Take the richest candidate rather than the first match — plenty of sites
    # have an empty `.content` wrapper sitting above the real article body.
    candidates = [soup.select_one(selector) for selector in CONTENT_SELECTORS]
    candidates.append(soup.body)
    bodies = [c for c in candidates if c is not None]
    if not bodies:
        return None
    body = max(bodies, key=lambda el: len(el.get_text(strip=True)))

    text = _clean_lines(body.get_text(separator="\n"))
    if len(text) < MIN_CHARS_WEB:
        logger.warning("Thin page: %s (%d chars)", source.ref, len(text))
        return None

    return Page(
        key=source.key,
        title=title,
        text=text,
        url=source.ref,
        tag=source.tag,
        domain=urlparse(source.ref).netloc,
    )


def fetch(source: Source, refresh: bool = False) -> Page | None:
    """Fetch one source, using the on-disk cache unless `refresh` is set."""
    path = _cache_path(source.key)
    if path.exists() and not refresh:
        return Page(**json.loads(path.read_text(encoding="utf-8")))

    try:
        if source.kind == "mediawiki":
            page = _fetch_mediawiki(source)
        else:
            page = _fetch_web(source)
    except Exception as exc:
        logger.warning("Fetch failed for %s: %s", source.key, exc)
        return None

    if page is None:
        return None

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(page.to_json(), ensure_ascii=False), encoding="utf-8")
    return page

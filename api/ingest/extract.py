"""Turn cleaned page text into structured corpus entries.

Scraped pages are messy and the old regex splitter could only ever recover
proverb-shaped lines. Here each chunk goes through the model once and comes
back as self-contained passages with a topic, a summary and the Igbo terms
they use — which is what lets the UI show real glossary terms and honest
source notes.

Extractions are cached by content hash, so a re-run costs nothing for chunks
that have not changed.
"""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass, field
from pathlib import Path

from api.config import EXTRACTION_MODEL, get_chat_model

from .fetch import Page

logger = logging.getLogger(__name__)

CACHE_DIR = Path(".cache/ingest/entries")
CHUNK_CHARS = 3500
CHUNK_OVERLAP = 250
MAX_ENTRIES_PER_CHUNK = 8

KINDS = {
    "proverb",
    "custom",
    "history",
    "language",
    "cosmology",
    "arts",
    "food",
    "general",
}

EXTRACTION_PROMPT = """You are building a retrieval corpus about Igbo culture, language, history and cosmology.

From the SOURCE TEXT below, extract every passage that carries real Igbo cultural knowledge. Discard navigation, adverts, author bios, comment threads, and anything not about Igbo matters.

Each entry must be:
- Self-contained. A reader who sees only this entry, with no other context, must understand it. Resolve pronouns and "as mentioned above" references.
- Faithful. Only state what the source text says. Do not add your own knowledge, and do not smooth over gaps.
- 40-120 words, in English, keeping Igbo words and their diacritics exactly as written (ị ụ ọ ń etc.).

For proverbs and idioms, keep the Igbo verbatim and give the translation and the meaning in the same entry.

Reply with a single JSON object:
{"entries": [{
  "text": "the self-contained passage",
  "topic": "3-6 words naming what this covers",
  "summary": "6-12 words describing what this passage covers",
  "kind": "one of: proverb, custom, history, language, cosmology, arts, food, general",
  "igbo_terms": [{"term": "Igbo word or phrase in the passage", "meaning": "short English gloss"}]
}]}

At most %d entries. Return {"entries": []} if the text carries nothing usable. Only list igbo_terms that actually appear in the entry's text; an empty list is fine.""" % MAX_ENTRIES_PER_CHUNK


@dataclass
class Entry:
    text: str
    topic: str
    summary: str
    kind: str
    igbo_terms: list[dict] = field(default_factory=list)
    page: Page | None = None


def chunk(text: str) -> list[str]:
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_CHARS,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    return [c for c in splitter.split_text(text) if len(c.strip()) >= 200]


def _cache_path(body: str) -> Path:
    digest = hashlib.sha256(f"{EXTRACTION_MODEL}\n{body}".encode("utf-8")).hexdigest()
    return CACHE_DIR / f"{digest[:24]}.json"


def _coerce(raw: dict) -> list[dict]:
    entries = raw.get("entries")
    if not isinstance(entries, list):
        return []

    cleaned = []
    for item in entries[:MAX_ENTRIES_PER_CHUNK]:
        if not isinstance(item, dict):
            continue
        text = str(item.get("text", "")).strip()
        if len(text) < 60:
            continue
        kind = str(item.get("kind", "general")).strip().lower()
        terms = [
            {
                "term": str(t.get("term", "")).strip(),
                "meaning": str(t.get("meaning", "")).strip(),
            }
            for t in (item.get("igbo_terms") or [])
            if isinstance(t, dict) and t.get("term") and t.get("meaning")
        ]
        cleaned.append(
            {
                "text": text,
                "topic": str(item.get("topic", "")).strip(),
                "summary": str(item.get("summary", "")).strip(),
                "kind": kind if kind in KINDS else "general",
                "igbo_terms": terms[:6],
            }
        )
    return cleaned


def extract_chunk(body: str, page: Page) -> list[Entry]:
    """Structure one chunk, reading through the on-disk cache."""
    path = _cache_path(body)
    if path.exists():
        raw = json.loads(path.read_text(encoding="utf-8"))
    else:
        try:
            response = get_chat_model(EXTRACTION_MODEL, temperature=0).invoke(
                [
                    ("system", EXTRACTION_PROMPT),
                    (
                        "user",
                        f"SOURCE: {page.title} ({page.domain})\n\nSOURCE TEXT:\n{body}",
                    ),
                ]
            )
            raw = _coerce(json.loads(str(response.content)))
        except Exception as exc:
            logger.warning("Extraction failed for %s: %s", page.title, exc)
            return []
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(raw, ensure_ascii=False), encoding="utf-8")

    return [Entry(page=page, **item) for item in raw]


def passthrough_chunk(body: str, page: Page) -> list[Entry]:
    """`--no-llm` path: keep the chunk verbatim with page-level metadata."""
    return [
        Entry(
            text=body.strip(),
            topic=page.title,
            summary=f"Passage from {page.title}",
            kind="general",
            igbo_terms=[],
            page=page,
        )
    ]

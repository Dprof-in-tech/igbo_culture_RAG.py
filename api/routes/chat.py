"""Retrieval and answer composition for Achalugo.

One turn produces one structured answer object:

    {"answer", "detail", "terms", "sources", "followups"}

`sources` are built from the documents retrieval actually returned — the model
is asked which numbered passages it leaned on, and those indices are mapped
back to real corpus metadata. The model never writes a citation itself.
"""

from __future__ import annotations

import json
import logging
import re
import time
from typing import Any, Iterable

from api.config import RETRIEVAL_K, get_chat_model, get_vector_store

logger = logging.getLogger(__name__)

MAX_SOURCES = 3
MAX_TERMS = 4
FOLLOWUPS = 2
SNIPPET_CHARS = 160

SYSTEM_PROMPT = """You are Achalugo, an Igbo woman elder and onye Amamihe (a person of wisdom), deeply rooted in Igbo culture. You answer questions about Igbo culture, tradition, customs, language, cosmology and history.

Voice: warm, first person, addressing the asker as a younger relative ("my dear", "nwa m"). Sprinkle real Igbo words naturally. Never condescend, never lecture at length.

Ground your answer in the numbered PASSAGES supplied. They are retrieved from an Igbo corpus. Prefer what they say over your own recollection, and never contradict them. If they are thin, you may draw on your own knowledge of Igbo culture, but do not invent specifics — names, dates, places, or ritual detail — that you are not confident of.

Always translate Igbo words and proverbs carefully; make sure the gloss genuinely matches the meaning.

If the question is not about Igbo matters, say so kindly in "answer" and steer back. Return no terms, no passage ids and no followups in that case.

Reply with a single JSON object and nothing else:
{"answer": "1-2 sentence direct answer in your voice",
 "detail": "2-4 sentences of depth, concrete and specific",
 "terms": [{"term": "Igbo word or phrase you used", "meaning": "short English gloss"}],
 "passage_ids": [1, 3],
 "followups": ["short natural next question", "another"]}

Rules: 1-4 terms, at most 3 passage_ids, exactly 2 followups. "passage_ids" must be numbers of PASSAGES above that genuinely informed the answer — leave it empty rather than pad it. Every term you list must be an Igbo word that appears in your answer or detail."""


# --- Retrieval --------------------------------------------------------------


RETRIEVAL_ATTEMPTS = 3
RETRIEVAL_BACKOFF = 0.4


def retrieve(query: str, k: int = RETRIEVAL_K) -> list:
    """Top-k corpus documents for a query.

    Never raises: an unreachable index degrades to an unsourced answer rather
    than a 500. Connection-level failures are retried, because a serverless
    cold start can hit a transient socket error reaching the Data API — the
    kind that succeeds immediately on a second try. Errors the API actually
    responded with (a missing collection, a bad token) are not retried, since
    repeating them only burns the request's time budget.
    """
    import httpx

    transient = (
        httpx.ConnectError,
        httpx.ConnectTimeout,
        httpx.ReadTimeout,
        httpx.RemoteProtocolError,
    )

    for attempt in range(RETRIEVAL_ATTEMPTS):
        try:
            return get_vector_store().similarity_search(query, k=k)
        except transient as exc:
            last = attempt == RETRIEVAL_ATTEMPTS - 1
            logger.warning(
                "Retrieval connection error (%d/%d): %s",
                attempt + 1,
                RETRIEVAL_ATTEMPTS,
                exc,
            )
            if last:
                logger.error("Retrieval unreachable; answering without corpus context")
                return []
            time.sleep(RETRIEVAL_BACKOFF * (2**attempt))
        except Exception:
            logger.exception("Retrieval failed; answering without corpus context")
            return []

    return []


def _passage_title(metadata: dict) -> str:
    for key in ("work", "source_title", "title", "domain"):
        value = metadata.get(key)
        if value:
            return str(value)
    return "Igbo corpus"


def _passage_note(document: Any) -> str:
    """A short line describing what the passage covers."""
    metadata = document.metadata or {}
    for key in ("summary", "topic"):
        value = metadata.get(key)
        if value:
            return str(value)
    text = " ".join((document.page_content or "").split())
    if len(text) > SNIPPET_CHARS:
        text = text[:SNIPPET_CHARS].rsplit(" ", 1)[0] + "…"
    return text


def format_passages(documents: Iterable[Any]) -> str:
    blocks = []
    for i, document in enumerate(documents, start=1):
        title = _passage_title(document.metadata or {})
        blocks.append(f"[{i}] ({title})\n{document.page_content}")
    return "\n\n".join(blocks)


def _sources_from(documents: list, passage_ids: list) -> list[dict]:
    """Map the model's passage numbers back onto real retrieved documents."""
    chosen = []
    for raw in passage_ids:
        try:
            index = int(raw) - 1
        except (TypeError, ValueError):
            continue
        if 0 <= index < len(documents):
            chosen.append(documents[index])

    # An answer that cited nothing still came out of the top of the index.
    if not chosen and documents:
        chosen = documents[:1]

    sources, seen = [], set()
    for document in chosen:
        metadata = document.metadata or {}
        title = _passage_title(metadata)
        url = metadata.get("source_url") or metadata.get("source")
        key = (title.lower(), url or "")
        if key in seen:
            continue
        seen.add(key)
        source = {"title": title, "note": _passage_note(document)}
        if url:
            source["url"] = url
        sources.append(source)
        if len(sources) >= MAX_SOURCES:
            break
    return sources


# --- Generation -------------------------------------------------------------


def _parse_json(raw: str) -> dict:
    """Tolerate a stray markdown fence around the JSON object."""
    text = raw.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?|```$", "", text, flags=re.MULTILINE).strip()
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("no JSON object in model response")
    return json.loads(text[start : end + 1])


def _clean_terms(raw: Any) -> list[dict]:
    terms, seen = [], set()
    for item in raw if isinstance(raw, list) else []:
        if not isinstance(item, dict):
            continue
        term = str(item.get("term", "")).strip()
        meaning = str(item.get("meaning", "")).strip()
        if not term or not meaning or term.lower() in seen:
            continue
        seen.add(term.lower())
        terms.append({"term": term, "meaning": meaning})
        if len(terms) >= MAX_TERMS:
            break
    return terms


def _clean_followups(raw: Any) -> list[str]:
    items = [str(q).strip() for q in raw] if isinstance(raw, list) else []
    return [q for q in items if q][:FOLLOWUPS]


def _to_messages(history: Any) -> list[tuple[str, str]]:
    """Prior turns as (role, content) pairs, oldest first."""
    turns = []
    for item in history if isinstance(history, list) else []:
        if not isinstance(item, dict):
            continue
        role = "assistant" if item.get("role") == "assistant" else "user"
        content = str(item.get("content", "")).strip()
        if content:
            turns.append((role, content))
    return turns[-6:]


def answer_question(query: str, history: Any = None) -> dict:
    """Retrieve, compose, and return one structured answer object."""
    documents = retrieve(query)

    if documents:
        context = format_passages(documents)
    else:
        context = "(No passages were retrieved. Answer from your own knowledge, and return an empty passage_ids.)"

    messages: list[tuple[str, str]] = [("system", SYSTEM_PROMPT)]
    messages.extend(_to_messages(history))
    messages.append(("user", f"PASSAGES:\n{context}\n\nQUESTION: {query}"))

    response = get_chat_model().invoke(messages)
    data = _parse_json(str(response.content))

    return {
        "answer": str(data.get("answer", "")).strip(),
        "detail": str(data.get("detail", "")).strip(),
        "terms": _clean_terms(data.get("terms")),
        "sources": _sources_from(documents, data.get("passage_ids") or []),
        "followups": _clean_followups(data.get("followups")),
    }

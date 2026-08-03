"""Build documents from extracted entries and write them to Astra."""

from __future__ import annotations

import hashlib
import logging

from .extract import Entry

logger = logging.getLogger(__name__)

BATCH = 100


def _embedding_text(entry: Entry) -> str:
    """What actually gets embedded.

    The Igbo terms are appended so a question asked with the Igbo word ("what
    is ọjị?") lands on the passage even when the body is mostly English.
    """
    parts = [entry.text]
    if entry.igbo_terms:
        glosses = "; ".join(
            f"{t['term']} — {t['meaning']}" for t in entry.igbo_terms
        )
        parts.append(f"Igbo terms: {glosses}")
    if entry.topic:
        parts.append(f"Topic: {entry.topic}")
    return "\n".join(parts)


def to_documents(entries: list[Entry]) -> tuple[list, list[str]]:
    """Documents plus deterministic ids, deduped on passage text.

    Ids are content hashes so re-running the pipeline overwrites rather than
    duplicating — the corpus can be grown incrementally.
    """
    from langchain_core.documents import Document

    documents, ids, seen = [], [], set()

    for entry in entries:
        page = entry.page
        if page is None:
            continue

        content = _embedding_text(entry)
        doc_id = hashlib.sha256(entry.text.strip().encode("utf-8")).hexdigest()[:32]
        if doc_id in seen:
            continue
        seen.add(doc_id)

        documents.append(
            Document(
                page_content=content,
                metadata={
                    "work": page.title,
                    "source_url": page.url,
                    "domain": page.domain,
                    "tag": page.tag,
                    "kind": entry.kind,
                    "topic": entry.topic,
                    "summary": entry.summary,
                    "igbo_terms": [t["term"] for t in entry.igbo_terms],
                    "content_type": "igbo_corpus",
                },
            )
        )
        ids.append(doc_id)

    return documents, ids


def write(documents: list, ids: list[str], collection: str | None = None) -> int:
    from api.config import get_vector_store

    store = get_vector_store(collection)
    written = 0
    for start in range(0, len(documents), BATCH):
        batch_docs = documents[start : start + BATCH]
        batch_ids = ids[start : start + BATCH]
        store.add_documents(batch_docs, ids=batch_ids)
        written += len(batch_docs)
        logger.info("Wrote %d/%d documents", written, len(documents))
    return written

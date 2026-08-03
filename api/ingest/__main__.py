"""CLI for the corpus ingestion pipeline.

    python3 -m api.ingest                     # full run
    python3 -m api.ingest --dry-run           # fetch + extract, write nothing
    python3 -m api.ingest --only proverbs     # one tag
    python3 -m api.ingest --no-llm            # skip the extraction pass
    python3 -m api.ingest --limit 5           # first N sources, for a smoke test

Fetches and extractions are cached under .cache/ingest, so re-runs are cheap
and interrupting a run loses nothing.
"""

from __future__ import annotations

import argparse
import logging
import sys
from collections import Counter
from concurrent.futures import ThreadPoolExecutor

from .extract import Entry, chunk, extract_chunk, passthrough_chunk
from .fetch import Page, fetch
from .load import to_documents, write
from .sources import SOURCES, TAGS, Source

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-7s %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("ingest")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="api.ingest", description=__doc__)
    parser.add_argument("--only", choices=TAGS, action="append", help="restrict to tag(s)")
    parser.add_argument("--limit", type=int, help="only the first N sources")
    parser.add_argument("--collection", help="override ASTRA_DB_COLLECTION_NAME")
    parser.add_argument("--dry-run", action="store_true", help="do not write to Astra")
    parser.add_argument("--no-llm", action="store_true", help="skip the extraction pass")
    parser.add_argument("--refresh", action="store_true", help="ignore the fetch cache")
    parser.add_argument("--workers", type=int, default=6, help="concurrent workers")
    return parser.parse_args()


def select(args: argparse.Namespace) -> list[Source]:
    chosen = SOURCES
    if args.only:
        chosen = [s for s in chosen if s.tag in set(args.only)]
    if args.limit:
        chosen = chosen[: args.limit]
    return chosen


def fetch_all(sources: list[Source], workers: int, refresh: bool) -> list[Page]:
    logger.info("Fetching %d sources", len(sources))
    with ThreadPoolExecutor(max_workers=workers) as pool:
        results = pool.map(lambda s: fetch(s, refresh=refresh), sources)
    pages = [page for page in results if page is not None]
    logger.info("Fetched %d/%d sources", len(pages), len(sources))
    return pages


def extract_all(pages: list[Page], workers: int, use_llm: bool) -> list[Entry]:
    jobs = [(body, page) for page in pages for body in chunk(page.text)]
    logger.info("Structuring %d chunks from %d pages", len(jobs), len(pages))

    worker = extract_chunk if use_llm else passthrough_chunk
    with ThreadPoolExecutor(max_workers=workers) as pool:
        batches = pool.map(lambda job: worker(*job), jobs)

    entries = [entry for batch in batches for entry in batch]
    logger.info("Extracted %d entries", len(entries))
    return entries


def report(entries: list[Entry], documents: list) -> None:
    by_kind = Counter(entry.kind for entry in entries)
    by_source = Counter(entry.page.title for entry in entries if entry.page)
    terms = {t["term"] for entry in entries for t in entry.igbo_terms}

    logger.info("--- corpus ---")
    logger.info("documents:    %d", len(documents))
    logger.info("igbo terms:   %d unique", len(terms))
    logger.info("sources:      %d", len(by_source))
    for kind, count in by_kind.most_common():
        logger.info("  %-10s %d", kind, count)
    logger.info("top sources:")
    for title, count in by_source.most_common(10):
        logger.info("  %-45s %d", title[:45], count)


def main() -> int:
    args = parse_args()
    sources = select(args)
    if not sources:
        logger.error("No sources selected")
        return 1

    pages = fetch_all(sources, args.workers, args.refresh)
    if not pages:
        logger.error("Nothing fetched; aborting")
        return 1

    entries = extract_all(pages, args.workers, use_llm=not args.no_llm)
    if not entries:
        logger.error("Nothing extracted; aborting")
        return 1

    documents, ids = to_documents(entries)
    report(entries, documents)

    if args.dry_run:
        logger.info("Dry run — nothing written.")
        for document in documents[:3]:
            logger.info("sample: %s", document.page_content[:180].replace("\n", " "))
        return 0

    written = write(documents, ids, args.collection)
    logger.info("Wrote %d documents to Astra", written)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

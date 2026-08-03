# Achalugo — Onye Amamihe

A retrieval-augmented chat where **Achalugo**, an Igbo elder persona, answers
questions about Igbo culture, tradition, customs, language and cosmology.

Every turn returns a **structured answer** rather than a wall of prose: a short
direct reply, supporting detail, the Igbo terms used with glosses, the corpus
documents the answer drew on, and two follow-up questions. Terms accumulate
into a running glossary for the session.

**Live:** https://igbo-culture-rag-py.vercel.app

---

## Architecture

```
app/  (Next.js, client)                  api/  (Flask, serverless)
┌──────────────────────┐                 ┌───────────────────────────────┐
│ Transcript           │  POST /api/chat │ index.py    validate, route   │
│ Composer             │ ──────────────▶ │ routes/chat.py                │
│ Glossary (derived)   │                 │   1. embed question           │
│                      │ ◀────────────── │   2. top-k from AstraDB       │
└──────────────────────┘  answer object  │   3. compose JSON answer      │
                                         │   4. map cited passages back  │
                                         │      to real source metadata  │
                                         └───────────────────────────────┘
```

`api/config.py` builds the embedding model and vector store for **both** the
serving path and the ingestion pipeline, so the write side and the read side
cannot drift onto different collections or dimensions.

### Tech

| Layer | What |
| --- | --- |
| Frontend | Next.js 13 App Router, TypeScript, Tailwind, Playfair Display + Work Sans |
| Backend | Flask, deployed as a Vercel Python function |
| Retrieval | AstraDB vector store via `langchain-astradb` |
| Models | OpenAI `text-embedding-3-small` (1536d), `gpt-4o-mini` for answers and ingestion |

---

## API

### `POST /api/chat`

```json
{
  "prompt": "Why do we break kola nut, and who may break it?",
  "history": [{ "role": "user", "content": "..." },
              { "role": "assistant", "content": "..." }]
}
```

`history` is optional; the client sends the last 6 turns.

**Response**

```json
{
  "answer": "1–2 sentence direct answer in Achalugo's voice",
  "detail": "2–4 sentences of depth",
  "terms":   [{ "term": "ọjị", "meaning": "kola nut" }],
  "sources": [{ "title": "Kola nut", "note": "role of kola in Igbo hospitality",
                "url": "https://en.wikipedia.org/wiki/Kola_nut" }],
  "followups": ["What words are said when breaking kola?", "May a woman break it?"],
  "request_id": "a1b2c3d4e5f6"
}
```

`detail`, `terms`, `sources` and `followups` are each optional — the UI renders
correctly when any subset is absent.

**`sources` are real retrieved documents.** The model is shown numbered
passages and asked which ones it leaned on; those indices are mapped back to
corpus metadata server-side. The model never writes a citation itself.

Failures return HTTP 500 but still carry a renderable in-character `answer`, so
the UI never has to show error chrome.

### `GET /api/health`

Reports whether the function can reach its config and its collection, and
whether that collection has any documents in it.

---

## Quick start

```bash
git clone https://github.com/Dprof-in-tech/igbo_culture_RAG.py.git
cd igbo_culture_RAG.py

pnpm install
pip install -r requirements.txt -r requirements-ingest.txt

cp .env.example .env      # then fill it in
```

Build the corpus (see below), then:

```bash
pnpm dev     # Next on :3000, Flask on :5328
```

---

## Corpus

The index is built by `api/ingest`, a four-stage pipeline over a registry of
**107 sources** — English and Igbo Wikipedia, Wikiquote, Britannica, and a set
of Igbo proverb and culture sites.

```
sources.py → fetch.py → extract.py → load.py
 registry    plaintext   LLM pass     chunk, embed, write
```

1. **Fetch.** Wikipedia and Wikiquote come through the MediaWiki API as clean
   plaintext, which is far better material than scraping rendered HTML. Other
   pages are fetched and reduced to text. Missing articles and dead links are
   logged and skipped.
2. **Extract.** Each ~3.5k-character chunk goes through `gpt-4o-mini` once and
   comes back as self-contained passages carrying a topic, a summary, a kind
   (`proverb`, `custom`, `history`, `language`, `cosmology`, `arts`, `food`)
   and the Igbo terms they use. Those terms are what feed the UI's glossary,
   and the summaries are what feed the "Ebe o si" source notes.
3. **Load.** Passages are embedded with their Igbo terms appended, so a
   question asked in Igbo lands on a passage whose body is mostly English.
   Document ids are content hashes, so re-running **overwrites rather than
   duplicates** — the corpus can be grown incrementally.

### Running it

```bash
python3 -m api.ingest                  # full run
python3 -m api.ingest --dry-run        # fetch + extract, write nothing
python3 -m api.ingest --only proverbs  # one tag (repeatable)
python3 -m api.ingest --limit 5        # first N sources, smoke test
python3 -m api.ingest --no-llm         # skip the extraction pass (free, noisier)
python3 -m api.ingest --refresh        # ignore the fetch cache
python3 -m api.ingest --collection x   # write somewhere other than the env default
```

Fetches and extractions are cached under `.cache/ingest/`, keyed by source and
by content hash. Re-runs cost no network and no OpenAI tokens for anything
unchanged, and interrupting a run loses nothing.

### Adding sources

Add entries to the appropriate group in `api/ingest/sources.py`. MediaWiki
titles resolve through redirects, so a near-miss title usually still lands —
it is worth listing a speculative article rather than leaving a gap.

---

## Deployment

Vercel serves the Next.js app and `api/index.py` as a Python function;
`vercel.json` routes `/api/*` into it. `requirements.txt` holds only what the
function needs at request time — scraping dependencies live in
`requirements-ingest.txt` and never enter the bundle.

Set every variable from `.env.example` in the Vercel project. Ingestion is run
locally, not on Vercel.

---

## Design

The interface follows the approved *editorial paper* direction: terracotta and
saffron on paper, Playfair Display for Achalugo's voice and Work Sans for
everything else, square edges throughout (the sole exception is the follow-up
pills), and no shadows — depth comes from 1px rules only. Desktop and mobile
are two discrete layouts that switch at 820px.

Igbo diacritics (`ị ụ ọ`) live in the Vietnamese Unicode block, so both fonts
load that subset — without it those characters fall back mid-word to a system
font.

---

## License

MIT. Traditional Igbo knowledge in the corpus is shared with attribution to its
community origins and remains the cultural heritage of the Igbo people.

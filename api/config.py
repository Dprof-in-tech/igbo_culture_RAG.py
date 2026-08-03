"""Shared configuration and lazily-built clients.

Both the serving path (`api.routes.chat`) and the ingestion pipeline
(`api.ingest`) build their vector store from here, so the write side and the
read side can never drift onto different collections or embedding models
again.

Everything is lazy: importing this module must not require credentials, or the
Flask app cannot even start to report a configuration error.
"""

from __future__ import annotations

import os
from functools import lru_cache

from dotenv import load_dotenv
from pydantic import SecretStr

load_dotenv()


class ConfigError(RuntimeError):
    """A required environment variable is missing."""


def _required(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise ConfigError(
            f"{name} is not set. Copy .env.example to .env and fill it in."
        )
    return value


# --- Models -----------------------------------------------------------------

# text-embedding-3-small at native 1536 dimensions on both sides. The previous
# code truncated query embeddings to 1024 while writing full-width vectors,
# which silently degraded every search.
EMBEDDING_MODEL = os.environ.get("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
EMBEDDING_DIMENSIONS = int(os.environ.get("OPENAI_EMBEDDING_DIMENSIONS", "1536"))

CHAT_MODEL = os.environ.get("OPENAI_CHAT_MODEL", "gpt-4o-mini")
EXTRACTION_MODEL = os.environ.get("OPENAI_EXTRACTION_MODEL", "gpt-4o-mini")

# --- Retrieval --------------------------------------------------------------

COLLECTION_NAME = os.environ.get("ASTRA_DB_COLLECTION_NAME", "igbo_corpus")
RETRIEVAL_K = int(os.environ.get("RETRIEVAL_K", "8"))


@lru_cache(maxsize=1)
def get_embeddings():
    from langchain_openai import OpenAIEmbeddings

    return OpenAIEmbeddings(
        api_key=SecretStr(_required("OPENAI_API_KEY")),
        model=EMBEDDING_MODEL,
        dimensions=EMBEDDING_DIMENSIONS,
    )


@lru_cache(maxsize=1)
def get_vector_store(collection_name: str | None = None):
    from langchain_astradb import AstraDBVectorStore

    return AstraDBVectorStore(
        collection_name=collection_name or COLLECTION_NAME,
        embedding=get_embeddings(),
        token=_required("ASTRA_DB_APPLICATION_TOKEN"),
        api_endpoint=_required("ASTRA_DB_API_ENDPOINT"),
        namespace=_required("ASTRA_DB_KEYSPACE_NAME"),
    )


@lru_cache(maxsize=2)
def get_chat_model(model: str | None = None, temperature: float = 0.4):
    from langchain_openai import ChatOpenAI

    return ChatOpenAI(
        api_key=SecretStr(_required("OPENAI_API_KEY")),
        model=model or CHAT_MODEL,
        temperature=temperature,
        model_kwargs={"response_format": {"type": "json_object"}},
    )

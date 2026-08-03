"""Flask entrypoint for the Achalugo RAG API."""

from __future__ import annotations

import logging
import sys
import uuid

from flask import Flask, jsonify, request
from pydantic import BaseModel, Field, ValidationError, field_validator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# In-character failure text, mirroring the client's own fallback so a server
# error still reads as Achalugo rather than as an error page.
VOICE_FAILURE = (
    "Forgive me, nwa m — my voice did not carry just then. "
    "Juo’m ajuju ọzọ, ask me again."
)


class Turn(BaseModel):
    role: str
    content: str


class Query(BaseModel):
    prompt: str = Field(min_length=1, max_length=2000)
    history: list[Turn] = Field(default_factory=list)

    @field_validator("prompt")
    @classmethod
    def _not_blank(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("prompt must not be blank")
        return stripped


def _handle_chat():
    request_id = uuid.uuid4().hex[:12]

    try:
        query = Query.model_validate(request.get_json(silent=True) or {})
    except ValidationError as exc:
        logger.warning("[%s] Invalid request: %s", request_id, exc)
        # include_context=False matters: a custom validator's ctx carries the
        # raw ValueError, which jsonify cannot serialise. include_input=False
        # keeps the caller's payload out of the response.
        details = exc.errors(
            include_url=False, include_context=False, include_input=False
        )
        return (
            jsonify(
                {
                    "error": "Invalid request",
                    "details": details,
                    "request_id": request_id,
                }
            ),
            400,
        )

    logger.info("[%s] Question: %.120s", request_id, query.prompt)

    try:
        # Imported here so a missing credential surfaces as a handled 500 with a
        # useful log line rather than killing the whole module at import time.
        from api.routes.chat import answer_question

        payload = answer_question(
            query.prompt,
            [turn.model_dump() for turn in query.history],
        )
    except Exception:
        logger.exception("[%s] Failed to answer", request_id)
        return (
            jsonify(
                {
                    "answer": VOICE_FAILURE,
                    "detail": "",
                    "terms": [],
                    "sources": [],
                    "followups": [],
                    "error": "Answer generation failed",
                    "request_id": request_id,
                }
            ),
            500,
        )

    logger.info(
        "[%s] Answered with %d source(s), %d term(s)",
        request_id,
        len(payload["sources"]),
        len(payload["terms"]),
    )
    payload["request_id"] = request_id
    return jsonify(payload)


# Registered on both paths: Vercel may or may not preserve the `/api` prefix
# when it routes into this function, depending on the rewrite in play.
app.add_url_rule("/api/chat", view_func=_handle_chat, methods=["POST"])
app.add_url_rule("/chat", view_func=_handle_chat, methods=["POST"], endpoint="chat_bare")


@app.route("/api/health", methods=["GET"])
@app.route("/health", methods=["GET"], endpoint="health_bare")
def health():
    """Reports whether the app can reach its config and its index."""
    try:
        from api.config import COLLECTION_NAME, get_vector_store

        # Deliberately not via routes.chat.retrieve, which swallows failures.
        hits = get_vector_store().similarity_search("kola nut", k=1)
        return jsonify(
            {
                "status": "ok",
                "collection": COLLECTION_NAME,
                "index_reachable": True,
                "index_has_documents": bool(hits),
            }
        )
    except Exception as exc:
        logger.exception("Health check failed")
        return jsonify({"status": "error", "details": str(exc)}), 500


@app.errorhandler(404)
def not_found(_error):
    return jsonify({"error": "Not found", "path": request.path}), 404


@app.errorhandler(405)
def method_not_allowed(_error):
    return (
        jsonify(
            {
                "error": "Method not allowed",
                "details": f"{request.method} is not allowed for {request.path}",
            }
        ),
        405,
    )

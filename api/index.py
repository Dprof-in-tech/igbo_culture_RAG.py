from flask import Flask,request, jsonify
from pydantic import BaseModel
from api.routes.chat import (
    build_full_prompt,
    send_to_openai
)
app = Flask(__name__)

class Query(BaseModel):
    prompt: str


@app.route("/api/chat", methods=['POST'])
def fill_and_send_prompt():
    data = request.get_json()
    prompt = data.get("prompt")
    docs = build_full_prompt(prompt)
    return jsonify({"text": send_to_openai(docs)})

# app.py
import os
from flask import Flask, request, jsonify
from agents.conversation_agent import ConversationAgent

app = Flask(__name__)

# Initialize once at startup
agent = ConversationAgent(
    model_name="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
    embed_model="togethercomputer/m2-bert-80M-8k-retrieval",
    index_name="wss-ai-memory"
)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json or {}
    user_msg = data.get("message", "")
    if not user_msg:
        return jsonify({"error":"no message provided"}), 400

    reply = agent.ask(user_msg)
    return jsonify({"reply": reply})

if __name__ == "__main__":
    # accessible on localhost:8000
    app.run(host="0.0.0.0", port=8000, debug=True)

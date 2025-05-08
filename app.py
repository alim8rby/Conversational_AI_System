import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from agents.conversation_agent import ConversationAgent

app = Flask(__name__, static_folder="static")
CORS(app)

agent = ConversationAgent(
    model_name="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
    embed_model="togethercomputer/m2-bert-80M-8k-retrieval",
    index_name="wss-ai-memory"
)

@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json or {}
    session = data.get("session")
    user_msg = data.get("message","")
    if not session or not user_msg:
        return jsonify({"error":"No session or message provided"}),400

    reply = agent.ask(session, user_msg)
    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)

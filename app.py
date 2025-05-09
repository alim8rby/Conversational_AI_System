import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

from agents.conversation_agent import ConversationAgent
from voice.voice_engine import VoiceEngine

app = Flask(__name__, static_folder="static")
CORS(app)

# Initialize the AI agent and VoiceEngine
agent = ConversationAgent(
    model_name="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
    embed_model="togethercomputer/m2-bert-80M-8k-retrieval",
    index_name="wss-ai-memory"
)
voice = VoiceEngine(lang="en")  # or 'ar' / 'franco' if you want to switch

@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data     = request.json or {}
    session  = data.get("session")
    user_msg = data.get("message", "")

    if not session or not user_msg:
        return jsonify({"error": "Session ID and message are required."}), 400

    # 1) Generate AI reply
    reply = agent.ask(session, user_msg)

    # 2) Synthesize voice and save under static/tts/{session}.mp3
    audio_path = f"static/tts/{session}.mp3"
    voice.text_to_speech(reply, audio_path)
    audio_url = f"/static/tts/{session}.mp3"

    # 3) Return both text and audio URL
    return jsonify({"reply": reply, "audio": audio_url})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)

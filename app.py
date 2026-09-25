"""
app.py

Flask backend for the Chemistry-only chatbot.
Uses the Gemini API to generate responses, guided by the system prompt
defined in chatbot_config.py.
"""

import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import google.generativeai as genai

from chatbot_config import SYSTEM_PROMPT

# Load environment variables from .env file
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL_NAME", "gemini-3.1-flash-lite")

if not GEMINI_API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is missing. Please set it in your .env file."
    )

# Configure the Gemini client
genai.configure(api_key=GEMINI_API_KEY)

# Create the model with the Chemistry-only system instruction
model = genai.GenerativeModel(
    model_name=GEMINI_MODEL_NAME,
    system_instruction=SYSTEM_PROMPT,
)

app = Flask(__name__)


@app.route("/")
def home():
    """Render the chat interface."""
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    """Receive a user message and return the chatbot's reply."""
    data = request.get_json(silent=True) or {}
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"reply": "Please type a Chemistry question."}), 400

    try:
        response = model.generate_content(user_message)
        reply_text = response.text if response and response.text else (
            "Sorry, I couldn't generate a response. Please try again."
        )
    except Exception as error:
        reply_text = f"An error occurred while contacting the AI service: {error}"

    return jsonify({"reply": reply_text})


if __name__ == "__main__":
    app.run(debug=True)

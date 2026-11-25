
from flask import Flask, request, jsonify, send_from_directory
from dotenv import load_dotenv
from google import genai
from google.genai import types
import os
import json

load_dotenv()

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# Generate content using Gemini
def generate(data):

    client = genai.Client(
        api_key=os.environ["GEMINI_API_KEY"]
    )

    result = client.models.generate_content(
        model=os.getenv(
            "GEMINI_MODEL", "gemini-3.5-flash-lite"
        ),
        contents=json.dumps(data, ensure_ascii=False),
        config=types.GenerateContentConfig(
            system_instruction=(
                "You are a professional product content agent. "
                "Generate high-quality marketing content. "
                "Use only supplied product facts. "
                "Do not invent product specifications or claims. "
                "Use INR for prices."
            )
        )
    )

    if not result.text:
        raise ValueError("Gemini returned no text")

    return result.text


# Load website
@app.get("/")
def home():
    return send_from_directory(BASE_DIR, "index.html")


# Load website assets
@app.get("/assets/<path:filename>")
def assets(filename):
    return send_from_directory(
        os.path.join(BASE_DIR, "assets"), filename
    )


# Check API configuration
@app.get("/api/status")
def status():
    return jsonify(
        live=bool(os.getenv("GEMINI_API_KEY")),
        provider="Gemini",
        model=os.getenv(
            "GEMINI_MODEL", "gemini-3.5-flash-lite"
        )
    )


# Generate AI content
@app.post("/api/generate")
def api():

    if not os.getenv("GEMINI_API_KEY"):
        return jsonify(error="Gemini API key missing"), 503

    data = request.get_json(silent=True)

    if not isinstance(data, dict) or not data:
        return jsonify(error="Product details missing"), 400

    try:
        return jsonify(text=generate(data))

    except Exception as e:
        app.logger.error(
            "Gemini generation failed: %s",
            type(e).__name__
        )
        return jsonify(
            error="Generation failed. Check Gemini model, API quota or configuration."
        ), 502


# Start website server
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000)

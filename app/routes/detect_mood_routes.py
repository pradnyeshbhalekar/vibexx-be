from flask import Blueprint, request, jsonify, make_response
import base64
from io import BytesIO
import numpy as np
import logging
import os
import json
from PIL import Image
from google import genai
from google.genai import types

# ---------------- Gemini (new SDK) ----------------

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

ALLOWED_EMOTIONS = ["calm", "happy", "sad", "angry"]

# ---------------- Helpers ----------------

def decode_base64_image(image_data: str) -> Image.Image:
    if "," in image_data:
        image_data = image_data.split(",")[1]
    img_bytes = base64.b64decode(image_data)
    return Image.open(BytesIO(img_bytes)).convert("RGB")


def map_emotion_to_mood(emotion: str) -> str:
    mapping = {
        "neutral": "calm",
        "happy": "happy",
        "sad": "sad",
        "angry": "angry",
        "fear": "angry",
        "disgust": "angry",
        "surprise": "calm",
    }
    return mapping.get(emotion, "calm")

# ---------------- Blueprint ----------------

detect_mood_routes = Blueprint(
    "detectmood",
    __name__,
    url_prefix="/api/detectmood"
)

# ---------------- FER route (lazy import as requested) ----------------

@detect_mood_routes.route("/", methods=["POST", "OPTIONS"])
def detect_mood():

    # 🔒 Lazy import (deployment-safe)
    try:
        from fer import FER
    except Exception:
        logging.exception("FER import failed")
        return jsonify({
            "error": "Emotion detection temporarily unavailable"
        }), 503

    try:
        data = request.get_json(silent=True)
        if not data or "image" not in data:
            return jsonify({"error": "Image data is missing"}), 400

        image = decode_base64_image(data["image"])
        image_np = np.array(image)

        detector = FER(mtcnn=False)
        emotion, score = detector.top_emotion(image_np)

        if not emotion:
            return jsonify({"error": "No emotion detected"}), 400

        return jsonify({
            "emotion": emotion,
            "mood": map_emotion_to_mood(emotion),
            "score": score
        }), 200

    except Exception:
        logging.exception("FER runtime error")
        return jsonify({"error": "Failed to process image"}), 500


@detect_mood_routes.route("/gemini", methods=["POST", "OPTIONS"])
def detect_mood_gemini():
    # Let Flask-CORS handle OPTIONS automatically
    if request.method == "OPTIONS":
        return "", 204

    try:
        data = request.get_json(silent=True)
        if not data or "image" not in data:
            return jsonify({"error": "Image missing"}), 400

        image = decode_base64_image(data["image"])

        img_buffer = BytesIO()
        image.save(img_buffer, format="JPEG")
        img_bytes = img_buffer.getvalue()

        prompt = """
You are a JSON API.

ONLY return valid JSON.
NO markdown.
NO explanation outside JSON.

Schema:
{
  "emotion": "calm" | "happy" | "sad" | "angry",
  "confidence": number between 0 and 1,
  "description": string
}
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                types.Content(
                    parts=[
                        types.Part.from_text(text=prompt),
                        types.Part.from_bytes(
                            data=img_bytes,
                            mime_type="image/jpeg"
                        )
                    ]
                )
            ],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.3
            )
        )

        if not response or not response.text:
            return jsonify({"error": "Empty response from Gemini"}), 500

        result = json.loads(response.text)

        emotion = result.get("emotion", "calm").lower()
        if emotion not in ALLOWED_EMOTIONS:
            emotion = "calm"

        confidence = float(result.get("confidence", 0.0))
        description = result.get("description", "Analysis unavailable")

        return jsonify({
            "emotion": emotion,
            "confidence": confidence,
            "description": description
        }), 200

    except Exception as e:
        logging.exception("Gemini mood detection failed")
        return jsonify({"error": "Mood detection failed"}), 500

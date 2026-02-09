from flask import Blueprint, request, jsonify
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
    if request.method == "OPTIONS":
        return jsonify({"ok": True}), 200

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

# ---------------- Gemini route (google-genai) ----------------

@detect_mood_routes.route("/gemini", methods=["POST"])
def detect_mood_gemini():
    try:
        data = request.get_json(silent=True)
        if not data or "image" not in data:
            return jsonify({"error": "Image missing"}), 400

        image = decode_base64_image(data["image"])

        prompt = """
Analyze the facial expression in the image.

Rules:
- Choose EXACTLY one emotion from: calm, happy, sad, angry
- Return a confidence between 0 and 1
- Write a short neutral explanation (1 sentence)

Return ONLY valid JSON:
{
  "emotion": "calm | happy | sad | angry",
  "confidence": number,
  "description": string
}
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                prompt,
                types.Part.from_image(image)
            ]
        )

        try:
            result = json.loads(response.text)
        except Exception:
            raise ValueError("Gemini returned invalid JSON")

        emotion = result.get("emotion", "calm").lower()
        if emotion not in ALLOWED_EMOTIONS:
            emotion = "calm"

        confidence = float(result.get("confidence", 0.5))
        confidence = max(0.0, min(1.0, confidence))

        description = str(result.get("description", "")).strip()

        return jsonify({
            "emotion": emotion,
            "confidence": confidence,
            "description": description
        }), 200

    except Exception:
        logging.exception("Gemini mood error")
        return jsonify({
            "emotion": "calm",
            "confidence": 0.5,
            "description": "Mood could not be confidently determined."
        }), 200
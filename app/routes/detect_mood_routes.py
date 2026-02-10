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


@detect_mood_routes.route("/gemini", methods=["POST"])
def detect_mood_gemini():
    try:
        data = request.get_json(silent=True)
        if not data or "image" not in data:
            return jsonify({"error": "Image missing"}), 400

        image = decode_base64_image(data["image"])

        # PIL → bytes
        img_buffer = BytesIO()
        image.save(img_buffer, format="JPEG")
        img_bytes = img_buffer.getvalue()

        prompt = """
        Analyze the facial expression in the image.
        
        Return a JSON object with this EXACT schema:
        {
          "emotion": "calm" | "happy" | "sad" | "angry",
          "confidence": number,
          "description": "short explanation"
        }
        """

        # --- FIXES START HERE ---
        response = client.models.generate_content(
            model="gemini-flash-latest",  # ✅ FIX 1: Use a valid model name
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
            # ✅ FIX 2: Force JSON response so you don't have to parse text manually
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.3 # Keep it deterministic
            )
        )

        if not response.text:
            raise ValueError("Empty response from Gemini")

        # Since we forced JSON mode, we can parse directly without regex/splitting
        result = json.loads(response.text)

        # Normalize data
        emotion = result.get("emotion", "calm").lower()
        if emotion not in ALLOWED_EMOTIONS:
            emotion = "calm"

        confidence = float(result.get("confidence", 0.5))
        description = result.get("description", "Analysis unavailable")

        return jsonify({
            "emotion": emotion,
            "confidence": confidence,
            "description": description
        }), 200

    except Exception as e:
        logging.error(f"Gemini API Error: {e}")
        # Return a fallback response so your frontend doesn't break
        return jsonify({
            "emotion": "calm",
            "confidence": 0.0,
            "description": "Could not verify mood (API Error)."
        }), 200 # Return 200 with fallback data, or 500 if you prefer
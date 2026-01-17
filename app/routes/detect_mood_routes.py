from flask import Blueprint, request, jsonify
from fer import FER
import base64
from io import BytesIO
import numpy as np
from google import genai
import logging
import os
from PIL import Image
import json

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))


ALLOWED_EMOTIONS = ["calm", "happy", "sad", "angry"]


    
def decode_image(image_data):
    image_data = image_data.split(',')[1]
    img_data = base64.b64decode(image_data)
    image = Image.open(BytesIO(img_data)).convert("RGB")
    return image



def map_emotion_to_mood(emotion: str):
    mapping = {
        "neutral": "calm",
        "happy": "happy",
        "sad": "sad",
        "angry": "angry",

        # extra emotions FER can return:
        "fear": "angry",       # fear usually = stress/anxiety → closer to angry
        "disgust": "angry",    # disgust = negative/high arousal → angry bucket
        "surprise": "calm"     # surprise is mixed, we make it calm by default
    }
    return mapping.get(emotion, "calm")  # fallback: calm

detect_mood_routes = Blueprint('detectmood', __name__, url_prefix='/api/detectmood')



@detect_mood_routes.route('/', methods=['POST','OPTIONS'])
def detect_mood():
    if request.method == "OPTIONS":
        return jsonify({"ok": True}), 200

    try:
        data = request.get_json(silent=True)

        if not data or "image" not in data:
            return jsonify({"error": "Image data is missing"}), 400

        img_base64 = data["image"]

        image = decode_image(img_base64)
        image_np = np.array(image)

        detector = FER(mtcnn=True)
        emotion, score = detector.top_emotion(image_np)

        if not emotion:
            return jsonify({"error": "No emotion detected"}), 400

        mood = map_emotion_to_mood(emotion)
        return jsonify({
            "emotion": emotion,
            "mood": mood,
            "score": score
        }), 200

    except Exception as e:
        logging.error(f"Error: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500


# gemini
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

Return ONLY valid JSON in this format:
{
  "emotion": "calm | happy | sad | angry",
  "confidence": number,
  "description": string
}
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[prompt, image],
        )

        # Gemini returns JSON as text
        try:
            result = json.loads(response.text)
        except Exception:
            raise ValueError("Gemini returned invalid JSON")

        # 🔒 Normalize
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
        })

    except Exception:
        logging.exception("Gemini mood error")
        return jsonify({
            "emotion": "calm",
            "confidence": 0.5,
            "description": "Mood could not be confidently determined."
        }), 200

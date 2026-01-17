from flask import Blueprint, request, session
from app.services.mood_engine import rank_tracks_by_mood
from app.services.reccobeats_service import get_audio_features


mood_routes = Blueprint(
    "mood_routes",
    __name__,
    url_prefix="/api/mood"
)


@mood_routes.route("/rank", methods=["POST"])
def rank_by_mood():
    data = request.get_json()
    mood = data.get("mood")

    if not mood:
        return {"error": "mood is required"}, 400

    track_ids = session.get("selected_tracks")
    if not track_ids:
        return {"error": "No selected tracks found"}, 400

    audio_features = get_audio_features(track_ids)

    ranked = rank_tracks_by_mood(audio_features, mood)

    return {
        "mood": mood,
        "count": len(ranked),
        "tracks": ranked[:30]
    }
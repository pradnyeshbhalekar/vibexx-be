from flask import Blueprint, request, jsonify
from app.services.spotify_service import get_spotify_client
from app.services.reccobeats_service import get_audio_features
import spotipy
from app.middleware.jwt_auth import require_jwt


track_routes = Blueprint('track_routes',__name__,url_prefix='/api/tracks')


@track_routes.route("/from-artists", methods=["POST"])
def get_tracks_from_artists():
    try:
        payload = require_jwt()

        data = request.get_json() or {}
        selected_artists = data.get("selected_artists")

        if not selected_artists or len(selected_artists) != 5:
            return {"error": "Exactly 5 selected artists required"}, 400

        sp = spotipy.Spotify(auth=payload["access_token"])

        track_map = {}

        for artist_id in selected_artists:
            results = sp.artist_top_tracks(artist_id)
            for track in results.get("tracks", []):
                track_map[track["id"]] = {
                    "id": track["id"],
                    "name": track["name"],
                    "artist": track["artists"][0]["name"],
                    "preview_url": track["preview_url"],
                    "popularity": track["popularity"],
                }

        tracks = list(track_map.values())[:50]

        return jsonify({
            "count": len(tracks),
            "tracks": tracks
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 401
from flask import Blueprint, request, jsonify
import spotipy
from app.middleware.jwt_auth import require_jwt

artist_routes = Blueprint("artist_routes", __name__, url_prefix="/api/artists")


@artist_routes.route("/top-30", methods=["GET"])
def get_top_artists():
    try:
        payload = require_jwt()  
        sp = spotipy.Spotify(auth=payload["access_token"])

        results = sp.current_user_top_artists(
            limit=30,
            time_range="medium_term"
        )

        artists = [
            {
                "id": artist["id"],
                "name": artist["name"],
                "image": artist["images"][0]["url"] if artist["images"] else None,
                "genre": artist["genres"],
                "popularity": artist["popularity"],
            }
            for artist in results["items"]
        ]

        return jsonify({
            "count": len(artists),
            "artists": artists
        })

    except Exception as e:
        print("[ERROR] Artist route error:", e)
        return jsonify({"error": str(e)}), 401


@artist_routes.route("/select", methods=["POST"])
def select_artists():
    try:
        payload = require_jwt() 

        data = request.get_json()
        artist_ids = data.get("artist_ids")

        if not isinstance(artist_ids, list):
            return {"error": "artist_ids must be a list"}, 400

        if len(artist_ids) != 5:
            return {"error": "Exactly 5 artists must be selected"}, 400



        return {
            "message": "Artists selected successfully",
            "selected_artists": artist_ids,
            "spotify_user_id": payload["spotify_user_id"]
        }

    except Exception as e:
        return jsonify({"error": str(e)}), 401
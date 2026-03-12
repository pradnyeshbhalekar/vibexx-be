from flask import Blueprint, request, jsonify
import spotipy
from app.middleware.jwt_auth import require_jwt

artist_routes = Blueprint("artist_routes", __name__, url_prefix="/api/artists")


@artist_routes.route("/top-30", methods=["GET"])
def get_top_artists():
    try:
        payload = require_jwt()
        access_token = payload.get("access_token")
        refresh_token = payload.get("refresh_token")

        sp = spotipy.Spotify(auth=access_token)

        try:
            # Test the token
            sp.current_user()
        except spotipy.SpotifyException as e:
            if e.http_status == 401 and refresh_token:
                # Token expired, try refreshing
                print("[INFO] Spotify access token expired, refreshing...")
                from app.utils.spotify_auth import get_spotify_oauth
                sp_oauth = get_spotify_oauth()
                token_info = sp_oauth.refresh_access_token(refresh_token)
                new_access_token = token_info.get("access_token")

                if new_access_token:
                    sp = spotipy.Spotify(auth=new_access_token)
                    print("[INFO] Token refreshed successfully.")
                    # Note: Ideally we'd update the JWT here, but for now we just use the fresh token for the request
                else:
                    raise Exception("Failed to refresh Spotify token")
            else:
                raise e

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
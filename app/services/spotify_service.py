import spotipy
from flask import session,jsonify
from app.utils.spotify_auth import get_spotify_oauth


def get_spotify_client():
    token_info = session.get("spotify_token")

    if not token_info:
        raise Exception("User not authenticated with Spotify")
    

    sp_oauth = get_spotify_oauth()
    if not sp_oauth:
        return jsonify({"error":"not authenticated"}),401

    if sp_oauth.is_token_expired(token_info):
        token_info = sp_oauth.refresh_access_token(token_info["refresh_token"])
        session["spotify_token"] = token_info

    return spotipy.Spotify(auth=token_info["access_token"])

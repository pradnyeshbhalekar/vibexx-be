from flask import Blueprint, redirect, request
import spotipy
from app.utils.spotify_auth import get_spotify_oauth
from app.utils.jwt_utils import create_jwt

auth_routes = Blueprint("auth_routes", __name__)

@auth_routes.route("/login")
def login():
    sp_oauth = get_spotify_oauth()
    return redirect(sp_oauth.get_authorize_url())


@auth_routes.route("/callback")
def callback():
    code = request.args.get("code")
    if not code:
        return "Missing code", 400

    sp_oauth = get_spotify_oauth()

    try:
        token_info = sp_oauth.get_access_token(code, as_dict=True)
    except Exception as e:
        return f"Spotify auth failed: {str(e)}", 400

    access_token = token_info.get("access_token")
    if not access_token:
        return "Failed to obtain access token", 500

    sp = spotipy.Spotify(auth=access_token)
    user = sp.current_user()

    jwt_token = create_jwt({
        "spotify_user_id": user["id"],
        "access_token": access_token,
        "refresh_token": token_info.get("refresh_token"),
    })

    return redirect(
        f"https://vibexx.onrender.com/top-artists?token={jwt_token}"
    )
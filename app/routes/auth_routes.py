from flask import Blueprint, redirect, request, session
from app.utils.spotify_auth import get_spotify_oauth
import urllib.parse
from app.utils.jwt import create_jwt


auth_routes = Blueprint("auth_routes", __name__)

@auth_routes.route("/login")
def login():
    session.clear()  
    sp_oauth = get_spotify_oauth()
    return redirect(sp_oauth.get_authorize_url())

@auth_routes.route("/callback")
def callback():
    sp_oauth = get_spotify_oauth()
    code = request.args.get("code")

    token_info = sp_oauth.get_access_token(code, as_dict=True)

    # Get Spotify user ID
    sp = spotipy.Spotify(auth=token_info["access_token"])
    user = sp.current_user()

    jwt_token = create_jwt({
        "spotify_user_id": user["id"],
        "access_token": token_info["access_token"],
        "refresh_token": token_info["refresh_token"],
    })

    # Redirect with token (temporary, we’ll improve later)
    frontend_redirect_url = "https://vibexx.onrender.com/top-artists"
    return redirect(f"{frontend_redirect_url}?token={jwt_token}")
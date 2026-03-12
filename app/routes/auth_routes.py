import os
from flask import Blueprint, redirect, request
import spotipy
from app.utils.spotify_auth import get_spotify_oauth
from app.utils.jwt import create_jwt

auth_routes = Blueprint("auth_routes", __name__)
FRONTEND_URL = os.getenv("FRONTEND_URL")

@auth_routes.route("/login")
def login():
    sp_oauth = get_spotify_oauth()
    return redirect(sp_oauth.get_authorize_url())


@auth_routes.route("/callback")
def callback():
    code = request.args.get("code")
    if not code:
        print("[ERROR] No code provided in Spotify callback")
        return "Missing code", 400

    sp_oauth = get_spotify_oauth()

    try:
        print("[INFO] Attempting to exchange code for token...")
        token_info = sp_oauth.get_access_token(code, as_dict=True)
        
        if not token_info:
            print("[ERROR] Spotify get_access_token returned None")
            return "Failed to obtain token info from Spotify", 500

        access_token = token_info.get("access_token")
        if not access_token:
            print("[ERROR] access_token missing from token_info")
            return "Failed to obtain access token", 500

        print("[INFO] Successfully obtained access token. Fetching user info...")
        sp = spotipy.Spotify(auth=access_token)
        user = sp.current_user()

        if not user or "id" not in user:
            print("[ERROR] Failed to fetch Spotify user info")
            return "Failed to fetch user info from Spotify", 500

        print(f"[INFO] Fetched Spotify user: {user['id']}")

        jwt_token = create_jwt({
            "spotify_user_id": user["id"],
            "access_token": access_token,
            "refresh_token": token_info.get("refresh_token"),
        })

        redirect_url = f"{FRONTEND_URL}/top-artists?token={jwt_token}"
        print(f"[INFO] Redirecting to: {redirect_url}")

        return redirect(redirect_url)

    except Exception as e:
        import traceback
        print("[ERROR] Exception in callback route:")
        traceback.print_exc()
        return f"Internal Server Error during authentication: {str(e)}", 500
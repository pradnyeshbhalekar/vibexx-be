from flask import Blueprint, redirect, request, session
from app.utils.spotify_auth import get_spotify_oauth
import urllib.parse

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
    error = request.args.get("error")

    frontend_redirect_url = "https://vibexx.onrender.com/top-artists"

    if error:
        return redirect(f"{frontend_redirect_url}?error={urllib.parse.quote(error)}")

    if not code:
        return redirect(f"{frontend_redirect_url}?error=no_code_received")


    sp_oauth.get_access_token(code, as_dict=True)

    session.permanent = True  
    print("SESSION AFTER CALLBACK:", list(session.keys()))

    return redirect(f"{frontend_redirect_url}?success=true")
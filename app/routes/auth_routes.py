from flask import Blueprint, redirect, request, session
from app.utils.spotify_auth import get_spotify_oauth
import urllib.parse

auth_routes = Blueprint("auth_routes", __name__, url_prefix='')

@auth_routes.route('/login')
def login():
    session.clear() 
    sp_oauth = get_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)


@auth_routes.route('/callback')
def callback():
    sp_oauth = get_spotify_oauth()
    code = request.args.get("code")
    error = request.args.get("error")

    frontend_redirect_url = "https://vibexx.onrender.com/top-artists"

    # Spotify error case
    if error:
        return redirect(f"{frontend_redirect_url}?error={urllib.parse.quote(error)}")

    if not code:
        return redirect(f"{frontend_redirect_url}?error=no_code_received")

    # Exchange code for token
    token_info = sp_oauth.get_access_token(code, as_dict=True)

    # Save in session
    session.permanent = True  # Make session persistent
    session["spotify_token"] = token_info
    session.modified = True  # Mark session as modified to ensure cookie is sent

    # ✅ Redirect to frontend with success
    return redirect(f"{frontend_redirect_url}?success=true")

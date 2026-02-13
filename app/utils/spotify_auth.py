from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import FlaskSessionCacheHandler
from flask import session
import os

def get_spotify_oauth():
    cache_handler = FlaskSessionCacheHandler(session)

    return SpotifyOAuth(
        client_id=os.getenv("SPOTIFY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
        redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"),
        scope="playlist-modify-private playlist-modify-public user-top-read",
        cache_handler=cache_handler,
        show_dialog=True
    )
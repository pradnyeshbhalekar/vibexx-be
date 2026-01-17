import os
from spotipy.oauth2 import SpotifyOAuth


def get_spotify_oauth():
    return SpotifyOAuth(
        client_id=os.getenv('SPOTIFY_CLIENT_ID'),
        client_secret=os.getenv('SPOTIFY_CLIENT_SECRET'),
        redirect_uri=os.getenv('SPOTIFY_REDIRECT_URI'),
        scope = 'playlist-modify-private playlist-modify-public user-top-read',
        cache_path=None,
        show_dialog=True
    )
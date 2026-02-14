import spotipy
from app.utils.spotify_auth import get_spotify_oauth

def get_spotify_client():
    sp_oauth = get_spotify_oauth()
    token_info = sp_oauth.get_cached_token()

    if not token_info:
        raise Exception("User not authenticated with Spotify")

    return spotipy.Spotify(auth=token_info["access_token"])
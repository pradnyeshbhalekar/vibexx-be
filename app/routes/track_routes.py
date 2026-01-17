from flask import Blueprint,session
from app.services.spotify_service import get_spotify_client
from app.services.reccobeats_service import get_audio_features

track_routes = Blueprint('track_routes',__name__,url_prefix='/api/tracks')


@track_routes.route('/from-artists',methods=['GET'])
def get_tracks_from_artists():
    selected_artists = session.get("selected_artists")

    if not selected_artists or len(selected_artists) != 5:
        return {
            "error":"Exactly 5 selected artists required"
        },400
    
    sp = get_spotify_client()

    track_map = {}

    for artist_id in selected_artists:
        results = sp.artist_top_tracks(artist_id)

        for track in results['tracks']:
            track_map[track['id']] = {
                "id":track['id'],
                "name":track['name'],
                "artist":track['artists'][0]['name'],
                "preview_url": track["preview_url"],
                "popularity":track["popularity"]
            }

    tracks = list(track_map.values())[:50]

    session['selected_tracks'] = [t["id"] for t in tracks]


    return {
        "Count":len(tracks),
        "Tracks": tracks
    }

@track_routes.route('/audio-features', methods=['GET'])
def get_tracks_audio_features():
    track_ids = session.get("selected_tracks")

    if not track_ids:
        return {"error": "No selected tracks found"}, 400


    audio_features = get_audio_features(track_ids)
    session["audio_features"] = audio_features
    session.modified = True

    return {
        "count": len(audio_features),
        "audio_features": audio_features
    }
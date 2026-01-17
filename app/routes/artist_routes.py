from flask import Blueprint,request,session,jsonify
from app.services.spotify_service import get_spotify_client

artist_routes = Blueprint('artist_routes',__name__,url_prefix='/api/artists')


@artist_routes.route('/top-30',methods=["GET"])
def get_top_artists():
    try:
        print(f"[DEBUG] Session keys: {list(session.keys())}")
        print(f"[DEBUG] Has spotify_token: {'spotify_token' in session}")
        
        sp = get_spotify_client()
        print(f"[DEBUG] Spotify client created successfully")
        

        results = sp.current_user_top_artists(
            limit=30,time_range='medium_term'
        )

        aritsts = []
        for artist in results["items"]:
            aritsts.append({
                "id":artist["id"],
                "name":artist['name'],
                "image":artist['images'][0]["url"] if artist['images'] else None,
                "genre":artist["genres"],
                "popularity":artist['popularity']
            })

        return{
            "count":len(aritsts),
            "artists":aritsts
        }
    except Exception as e:
        print(f"[ERROR] Artist route error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 401


@artist_routes.route('/select',methods=['POST'])
def select_artists():
    data = request.get_json()

    if not data or 'artist_ids' not in data:
        return {'error':'artist_ids is required'},400
    
    artist_ids = data['artist_ids']

    if not isinstance(artist_ids,list):
        return {"error":"artist_ids must be in a list"},400
    
    if len(artist_ids) !=5:
        return {"error":"5 artist must be selected"},400
    
    session['selected_artists'] = artist_ids

    return {
        "message":"Artists selected successfully",
        "selected_artists": artist_ids
    }
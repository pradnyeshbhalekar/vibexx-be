from flask import Flask,session,jsonify,request
from flask_cors import CORS
from dotenv import load_dotenv
import os


def create_app():
    load_dotenv()

    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
    app.config.update(
    SESSION_COOKIE_SAMESITE="None",
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_NAME="vibexx_session",
    SESSION_COOKIE_DOMAIN=None, 
    PERMANENT_SESSION_LIFETIME=86400 * 7  
)

    # Configure CORS first
    CORS(
        app,
        resources={r"/*": {"origins": ["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5000", "http://127.0.0.1:5000"]}},
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        expose_headers=["Content-Type"]
    )


    from app.routes.auth_routes import auth_routes
    from app.routes.artist_routes import artist_routes
    from app.routes.track_routes import track_routes
    from app.routes.mood_routes import mood_routes
    from app.routes.playlist_routes import playlist_routes
    from app.routes.detect_mood_routes import detect_mood_routes

    app.register_blueprint(auth_routes)
    app.register_blueprint(artist_routes)
    app.register_blueprint(track_routes)
    app.register_blueprint(mood_routes)
    app.register_blueprint(playlist_routes)
    app.register_blueprint(detect_mood_routes)


    @app.route("/health")
    def health():
        return {"status": "ok"}
    
    @app.route("/debug/session")
    def debug_session():

        return {
        "keys": list(session.keys()),
        "has_spotify_token": "spotify_token" in session,
        "spotify_token": session.get("spotify_token"),
        "audio_features_type": str(type(session.get("audio_features"))),
        "audio_features_len": len(session.get("audio_features", [])) if isinstance(session.get("audio_features"), list) else None
        }
    
    @app.route("/mood", methods=["POST"])
    def receive_mood():
        data = request.get_json()

        mood = data.get("mood")
        energy = data.get("energyLevel")
        description = data.get("description")

        if not mood or energy is None:
            return jsonify({"error": "Invalid mood payload"}), 400

        session["mood"] = mood

        print("Mood received:", mood, energy, description)
        return jsonify({"success": True}) 
    
    


    return app
import requests

BASE_URL = "https://api.reccobeats.com/v1"
MAX_IDS_PER_REQUEST = 30


def chunk_list(items, size):
    for i in range(0, len(items), size):
        yield items[i:i + size]


def extract_spotify_id(href):
    # href looks like: https://open.spotify.com/track/{id}
    return href.split("/track/")[-1]


def get_audio_features(track_ids):
    all_features = []

    for chunk in chunk_list(track_ids, MAX_IDS_PER_REQUEST):
        response = requests.get(
            f"{BASE_URL}/audio-features",
            params={"ids": ",".join(chunk)}
        )

        if response.status_code != 200:
            raise Exception(
                f"ReccoBeats error {response.status_code}: {response.text}"
            )

        data = response.json()

        for item in data.get("content", []):
            all_features.append({
                "spotify_id": extract_spotify_id(item["href"]),
                "acousticness": item["acousticness"],
                "danceability": item["danceability"],
                "energy": item["energy"],
                "instrumentalness": item["instrumentalness"],
                "liveness": item["liveness"],
                "loudness": item["loudness"],
                "speechiness": item["speechiness"],
                "tempo": item["tempo"],
                "valence": item["valence"],
                "key": item["key"],
                "mode": item["mode"]
            })

    return all_features

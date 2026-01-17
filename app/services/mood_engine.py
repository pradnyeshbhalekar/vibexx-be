from app.services.moodmapping import MOOD_PROFILES
from app.services.mood_rules import passes_gate


def percentile(sorted_vals,v):
    if not sorted_vals:
        return 0
    
    return sorted_vals.index(v) /len(sorted_vals)

def score_track(track,weights):
    score = 0.0
    for feature, weight in weights.items():
        value = track.get(feature)
        if value is None:
            continue
        score += value * weight

    return round(score,4)

def rank_tracks_by_mood(audio_features, mood):
    profile = MOOD_PROFILES[mood]
    weights = profile["weights"]


    valences = sorted(t["valence"] for t in audio_features if "valence" in t)
    energies = sorted(t["energy"] for t in audio_features if "energy" in t)

    ranked = []

    for t in audio_features:
        if not passes_gate(t, mood):
            continue


        if "valence" not in t or "energy" not in t:
            continue

        vp = percentile(valences, t["valence"]) if valences else 0.5
        ep = percentile(energies, t["energy"]) if energies else 0.5


        if mood == "sad" and (vp > 0.55 or ep > 0.65):
            continue
        if mood == "calm" and ep > 0.55:
            continue
        if mood == "focus" and not (0.3 <= ep <= 0.75):
            continue
        if mood == "angry" and (ep < 0.60 or vp > 0.55):
            continue

        score = score_track(t, weights)

        # penalties
        if mood == "sad" and t.get("danceability", 0) > 0.7:
            score -= 0.25
        if mood == "calm" and t.get("valence", 0) < 0.25:
            score -= 0.2
        if mood == "focus" and t.get("danceability", 0) > 0.65:
            score -= 0.25
        if mood == "angry" and t.get("valence", 0) > 0.6:
            score -= 0.3

        ranked.append({**t, "mood_score": round(score, 4)})

    ranked.sort(key=lambda x: x["mood_score"], reverse=True)
    return ranked

from app.services.moodmapping import MOOD_PROFILES

def looks_happy(t):
    return t.get("valence",0) >= 0.6 and t.get("energy",0) >= 0.6

def looks_sad(t):
    return t.get("valence",1) >= 0.35 and t.get("energy",0) <= 0.5

def looks_angry(t):
    return t.get("energy",0) >= 0.75 and t.get("valence",1) <= 0.45

def looks_calm(t):
    return t.get("energy",1) <=0.4 and t.get("tempo",200) <= 100



def passes_gate(track, mood):
    valence = track.get("valence", 0.5)
    energy = track.get("energy", 0.5)
    tempo = track.get("tempo", 120)
    dance = track.get("danceability", 0.5)
    instr = track.get("instrumentalness", 0.0)

    if mood == "happy":
        return looks_happy(track)

    if mood == "sad":
        if looks_happy(track) or looks_angry(track):
            return False

        return (
            valence <= 0.55 and
            energy <= 0.70 and
            tempo <= 140
        )

    if mood == "calm":
        if looks_happy(track) or looks_angry(track):
            return False

        return (
            energy <= 0.65 and
            tempo <= 130
        )

    if mood == "focus":
        if looks_happy(track) or looks_sad(track):
            return False

        return (
            energy <= 0.75 and
            dance <= 0.70 and
            instr >= 0.05
        )

    if mood == "angry":
        if looks_happy(track) or looks_calm(track):
            return False


        return (
            energy >= 0.60 and
            tempo >= 110
        )

    return True

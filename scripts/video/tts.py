#!/usr/bin/env python3
"""
Voiceover ElevenLabs per il motore video. Una traccia MP3 per scena.

SECRET: la API key NON sta nel repo. Passala via variabile d'ambiente:
    export ELEVENLABS_API_KEY="sk_..."
Voce di default: "Eric - Smooth, Trustworthy" (buona resa IT sul modello multilingua).
"""
import os, json, subprocess, urllib.request, urllib.error

DEFAULT_VOICE = "cjVigY5qzO86Huf0OWal"   # Eric
MODEL = "eleven_multilingual_v2"

def synth(segments, out_dir, voice_id=DEFAULT_VOICE, api_key=None):
    """segments: dict {sid: testo}. Ritorna {sid: durata_sec}. Scrive out_dir/<sid>.mp3."""
    api_key = api_key or os.environ.get("ELEVENLABS_API_KEY")
    if not api_key:
        raise SystemExit("Manca ELEVENLABS_API_KEY (export ELEVENLABS_API_KEY=sk_...).")
    os.makedirs(out_dir, exist_ok=True)
    durations = {}
    for sid, text in segments.items():
        body = json.dumps({
            "text": text, "model_id": MODEL,
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.75, "style": 0.0, "use_speaker_boost": True},
        }).encode()
        req = urllib.request.Request(
            f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}?output_format=mp3_44100_128",
            data=body, method="POST",
            headers={"xi-api-key": api_key, "Content-Type": "application/json", "Accept": "audio/mpeg"})
        with urllib.request.urlopen(req, timeout=120) as r:
            data = r.read()
        mp3 = os.path.join(out_dir, f"{sid}.mp3")
        open(mp3, "wb").write(data)
        out = subprocess.run(["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
                              "-of", "csv=p=0", mp3], capture_output=True, text=True).stdout.strip()
        durations[sid] = round(float(out), 3)
        print(f"  [tts] {sid}: {durations[sid]}s")
    json.dump(durations, open(os.path.join(out_dir, "durations.json"), "w"), indent=1)
    return durations

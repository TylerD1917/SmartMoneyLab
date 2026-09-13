#!/usr/bin/env python3
"""
Driver: costruisce il video YouTube di UN articolo (opt-in).

    python scripts/video/build_video.py <slug> [--no-intro] [--reuse-audio]

Richiede una config in scripts/video/configs/<slug>.py con una variabile CONFIG.
Genera:
    social/<slug>/video_youtube.mp4              (con intro, senza musica)
    social/<slug>/video_youtube_nointro.mp4      (solo contenuto)
Audio e frame intermedi in una cartella temporanea, non committata.

Note:
- La musica NON viene aggiunta qui: si mette dopo (Canva o traccia libera). Il video
  esce SENZA musica di sottofondo, pronto per il montaggio audio.
- L'intro standard di brand va generata una volta con intro.py -> social/_brand/intro_smartmoneylab.mp4
  e viene anteposta se presente (a meno di --no-intro).
- SECRET: export ELEVENLABS_API_KEY prima di lanciare (a meno di --reuse-audio).
"""
import os, sys, json, importlib.util, subprocess, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import engine, tts

def load_config(slug):
    path = os.path.join(HERE, "configs", f"{slug}.py")
    if not os.path.exists(path):
        raise SystemExit(f"Nessuna config per '{slug}': {path} non esiste (il video è opt-in).")
    spec = importlib.util.spec_from_file_location(f"cfg_{slug}", path)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod.CONFIG

def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags = set(a for a in sys.argv[1:] if a.startswith("--"))
    if not args: raise SystemExit("Uso: build_video.py <slug> [--no-intro] [--reuse-audio]")
    slug = args[0]
    cfg = load_config(slug)
    charts_dir = os.path.join(ROOT, cfg.get("charts_dir", f"public/charts/{slug}"))
    out_dir = os.path.join(ROOT, "social", slug); os.makedirs(out_dir, exist_ok=True)
    work = os.path.join(tempfile.gettempdir(), f"smlvideo_{slug}"); os.makedirs(work, exist_ok=True)

    # scene ids
    scenes = cfg["scenes"]
    for i, sc in enumerate(scenes): sc["_sid"] = f"s{i+1}"
    segments = {sc["_sid"]: sc["narration"] for sc in scenes}

    if "--reuse-audio" in flags and os.path.exists(os.path.join(work, "durations.json")):
        durations = json.load(open(os.path.join(work, "durations.json")))
        print("[audio] riuso tracce esistenti")
    else:
        print("[audio] genero voiceover ElevenLabs...")
        durations = tts.synth(segments, work, voice_id=cfg.get("voice_id", tts.DEFAULT_VOICE))

    core = os.path.join(out_dir, "video_youtube_nointro.mp4")
    print("[render] scene + montaggio...")
    engine.build(cfg, durations, work, core, charts_dir)

    intro = os.path.join(ROOT, "social", "_brand", "intro_smartmoneylab.mp4")
    if "--no-intro" in flags or not os.path.exists(intro):
        final = core
        if not os.path.exists(intro) and "--no-intro" not in flags:
            print(f"[intro] assente ({intro}): salto. Genera con intro.py per averla.")
    else:
        final = os.path.join(out_dir, "video_youtube.mp4")
        listf = os.path.join(work, "concat_intro.txt")
        open(listf, "w").write(f"file '{intro}'\nfile '{core}'\n")
        subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", listf,
                        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "19", "-preset", "medium",
                        "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", final],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"[ok] {final}")

if __name__ == "__main__":
    main()

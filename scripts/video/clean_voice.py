#!/usr/bin/env python3
"""Pulizia delle tracce vocali registrate a mano, per la pipeline video.

Catena, in quest'ordine:
  1. un solo canale (le registrazioni da telefono sono mono duplicato)
  2. passa-alto 85 Hz: toglie rumble, maneggiamento, pop delle esplosive
  3. guadagno fisso +18 dB: le tracce arrivano molto sotto il livello utile
  4. riduzione rumore leggera: la stanza e' gia' silenziosa, spingere darebbe artefatti
  5. compressione gentile: livella le frasi senza schiacciare
  6. loudnorm a due passate: -16 LUFS, true peak -1.5 dBTP
  7. taglio dell'annuncio di scena iniziale e dei silenzi ai bordi

Uso: python3 clean_voice.py <cartella_tracce> [--out <cartella>]
"""
import json, re, subprocess, sys
from pathlib import Path

TARGET_I, TARGET_TP, TARGET_LRA = -16.0, -1.5, 11.0
PREGAIN_DB = 18
SCENES = [f"s{i}" for i in range(1, 9)]
CUT_SLATE = True


def run(args):
    return subprocess.run(args, capture_output=True, text=True)


def ff(*args):
    return run(["ffmpeg", "-hide_banner", "-nostats", "-y", *args])


def dur(p):
    o = run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "csv=p=0", str(p)]).stdout.strip()
    return float(o) if o else 0.0


PRE = (f"pan=mono|c0=c0,highpass=f=85,volume={PREGAIN_DB}dB,"
       "afftdn=nr=12:nf=-52,"
       "acompressor=threshold=-20dB:ratio=2.5:attack=15:release=250")


def silences(wav, thresh="-30dB", mind=0.30):
    """Intervalli di silenzio (start, end) rilevati sulla traccia normalizzata."""
    r = ff("-i", str(wav), "-af", f"silencedetect=noise={thresh}:d={mind}", "-f", "null", "-")
    out, start = [], None
    for m in re.finditer(r"silence_(start|end): ([0-9.]+)", r.stderr):
        if m.group(1) == "start":
            start = float(m.group(2))
        elif start is not None:
            out.append((start, float(m.group(2)))); start = None
    total = dur(wav)
    if start is not None:
        out.append((start, total))
    return out, total


def trim_points(wav, cut_slate=True):
    """Inizio e fine del parlato utile.

    Se cut_slate, salta l'annuncio di scena iniziale ("scena tre"): e' il primo
    frammento breve, seguito da una pausa piena, dentro i primi secondi.
    Con registrazioni senza annuncio va passato --no-slate, altrimenti la
    prima frase verrebbe tagliata.
    """
    sil, total = silences(wav)
    slate = None
    start = 0.0
    rest = sil
    if sil and sil[0][0] < 0.25:            # silenzio iniziale
        start = sil[0][1]
        rest = sil[1:]
    if cut_slate:
        for a, b in rest:
            if a > 8.0:
                break
            if (a - start) < 3.5:            # frammento breve = annuncio
                slate = (start, a)
                start = b
                break
    end = total
    if sil and abs(sil[-1][1] - total) < 0.10 and sil[-1][0] > start:
        end = sil[-1][0]
    return max(0.0, start - 0.25), min(total, end + 0.35), slate, total


def main():
    global CUT_SLATE
    CUT_SLATE = "--no-slate" not in sys.argv
    src = Path(sys.argv[1]).expanduser()
    out = Path(sys.argv[sys.argv.index("--out") + 1]) if "--out" in sys.argv else src / "pulite"
    out.mkdir(parents=True, exist_ok=True)
    tmp = Path("/tmp/voceclean"); tmp.mkdir(exist_ok=True)

    report = []
    for sid in SCENES:
        srcf = next((src / f"{sid}{e}" for e in (".mp4", ".m4a", ".wav", ".mp3", ".aac")
                     if (src / f"{sid}{e}").exists()), None)
        if srcf is None:
            print(f"[!] {sid}: file non trovato"); continue

        a, b = tmp / f"{sid}_a.wav", tmp / f"{sid}_b.wav"
        ff("-i", str(srcf), "-af", PRE, "-ar", "48000", "-c:a", "pcm_s16le", str(a))

        # loudnorm: misura poi applica
        r = ff("-i", str(a), "-af",
               f"loudnorm=I={TARGET_I}:TP={TARGET_TP}:LRA={TARGET_LRA}:print_format=json",
               "-f", "null", "-")
        m = json.loads(re.search(r"\{[^{}]*\}", r.stderr, re.S).group(0))
        ff("-i", str(a), "-af",
           f"loudnorm=I={TARGET_I}:TP={TARGET_TP}:LRA={TARGET_LRA}:"
           f"measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
           f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:"
           f"offset={m['target_offset']}:linear=true:print_format=summary",
           "-ar", "48000", "-c:a", "pcm_s16le", str(b))

        start, end, slate, total = trim_points(b, cut_slate=CUT_SLATE)

        mp3 = out / f"{sid}.mp3"
        ff("-i", str(b), "-ss", f"{start:.3f}", "-to", f"{end:.3f}",
           "-c:a", "libmp3lame", "-b:a", "192k", "-ar", "44100", str(mp3))

        report.append(dict(sid=sid, src=srcf.name, dur_in=round(dur(srcf), 2),
                           dur_out=round(dur(mp3), 2),
                           I_in=m["input_i"], tagliato_inizio=round(start, 2),
                           annuncio=f"{slate[0]:.2f}-{slate[1]:.2f}s" if slate else "no"))
        print(f"  [{sid}] {dur(srcf):6.2f}s -> {dur(mp3):6.2f}s   "
              f"annuncio tagliato: {'si' if slate else 'no'}")

    json.dump({r["sid"]: r["dur_out"] for r in report},
              open(out / "durations.json", "w"), indent=1)
    json.dump(report, open(out / "report_pulizia.json", "w"), indent=1, ensure_ascii=False)
    tot = sum(r["dur_out"] for r in report)
    print(f"\ntotale parlato pulito: {tot:.1f}s ({tot/60:.2f} min)")
    print("scritti in", out)


if __name__ == "__main__":
    main()

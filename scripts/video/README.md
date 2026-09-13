# Pipeline video YouTube — SmartMoneyLab

Trasforma un articolo in un video explainer "faceless" data-viz (16:9, 1080p, voce IT).
**Opt-in**: un video si crea SOLO per gli articoli che hanno una config in `configs/<slug>.py`.
Nessuna GitHub Action, nessuna generazione automatica: si lancia a mano quando vuoi.

## Requisiti
- Python 3 con `pillow` e (per la musica opzionale) `numpy`
- `ffmpeg` + `ffprobe` nel PATH
- **Secret** (solo per la voce): `export ELEVENLABS_API_KEY="sk_..."` — la key NON sta nel repo.

## Uso
```bash
# 1) genera UNA volta l'intro di brand (riusata da tutti i video)
python scripts/video/intro.py            # -> social/_brand/intro_smartmoneylab.mp4

# 2) costruisci il video di un articolo (deve esistere configs/<slug>.py)
export ELEVENLABS_API_KEY="sk_..."
python scripts/video/build_video.py mutuo-fisso-o-variabile
```
Output in `social/<slug>/`:
- `video_youtube.mp4` — con intro, **senza musica** (pronto per aggiungere la traccia in Canva)
- `video_youtube_nointro.mp4` — solo contenuto

Flag: `--no-intro` (salta l'intro), `--reuse-audio` (riusa il voiceover già generato, niente TTS/costi).

## Creare il video di un nuovo articolo
1. Genera prima i grafici dell'articolo (come sempre) in `public/charts/<slug>/`.
2. Copia `configs/mutuo-fisso-o-variabile.py` in `configs/<slug>.py` e adatta le scene.
3. `python scripts/video/build_video.py <slug>`.

Ogni scena ha: `type`, contenuti specifici, `narration` (testo letto dalla voce, numeri in
lettere per una resa TTS pulita) e `captions` (sottotitoli brevi a schermo).

Tipi di scena (vedi `engine.py`):
- `cover` — apertura (+ sparkline fisso/variabile opzionale)
- `chart_side` — grafico reale a sinistra + annotazioni a destra (mai testo sopra i grafici)
- `stats` — grandi numeri con count-up + inset grafico opzionale
- `risk_bars` — stat % + barre "shock" (a→b, +X%)
- `transform_chart` — "A%→B%" (count-up) poi crossfade su un grafico
- `rates_today` — due chip tasso a confronto + badge + riga count-up + CTA
- `outro` — card brand finale (logo, tagline, handle, disclaimer)

## Musica e copertina
- **Musica**: non viene aggiunta qui. Si mette dopo (Canva o traccia libera/ambient AI).
  `music.py <secondi>` genera un pad ambient originale opzionale (poi si mixa con ducking se serve).
- **Copertina**: si fa in Canva. Logo/watermark pronti in `social/_brand/`.

## Note tecniche / gotcha
- Le scene sono renderizzate con Pillow e inviate in pipe a ffmpeg (niente migliaia di PNG su disco).
- I grafici dell'articolo hanno già titolo+legenda: **non** sovrapporre testo, usa `chart_side`/`inset`.
- Frame e audio intermedi vivono in `<tmp>/smlvideo_<slug>/` (fuori dal repo).
- Riproducibile: cambi testo/grafici nella config e rilanci.
```

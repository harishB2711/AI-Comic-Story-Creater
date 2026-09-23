# ComicCraft — Fast Build

This version is optimized for fast comic generation.

## What changed

- One Gemini request for outline + narration/dialogue instead of two.
- Hugging Face remote image generation using `black-forest-labs/FLUX.1-schnell` instead of loading Stable Diffusion locally.
- Three panel image requests run concurrently.
- FLUX.1-schnell uses 4 inference steps.
- The existing `.env` names (`HF_TOKEN`, `HF_IMAGE_MODEL`, `IMAGE_BACKEND`, `PANELS_PER_COMIC`) are now read correctly.
- The obsolete `gemini-2.5-flash` fallback is removed.

## Setup

Keep your existing `.env` file; do not share it.

```powershell
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/`.

Expected `.env` values:

```text
GEMINI_API_KEY=...
GEMINI_OUTLINE_MODEL=gemini-3.8-flash
GEMINI_STORY_MODEL=gemini-3.8-flash
HF_TOKEN=...
IMAGE_BACKEND=hf
HF_IMAGE_MODEL=black-forest-labs/FLUX.1-schnell
IMAGE_STEPS=4
IMAGE_WIDTH=768
IMAGE_HEIGHT=512
PANELS_PER_COMIC=5
DEV_FALLBACK=false
```

`requirements-local.txt` is only for an optional local diffusion backend and is not needed for the fast build.


## Ultra-fast mode

Fast Mode is enabled by default: 4 panels, 512x384 images, 4 inference steps, and all panel image requests are sent concurrently. In your `.env`, use `FAST_MODE=true`. If you want the older 5-panel behavior, set `FAST_MODE=false` and `PANELS_PER_COMIC=5`.

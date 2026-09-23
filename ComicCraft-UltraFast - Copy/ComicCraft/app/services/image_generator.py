from pathlib import Path
from textwrap import shorten
from PIL import Image, ImageDraw

from app.config import get_settings
from app.utils.text import safe_filename


def _hf_image(prompt: str) -> Image.Image:
    settings = get_settings()
    if not settings.hf_api_key:
        raise RuntimeError("HF_TOKEN is not configured.")

    try:
        from huggingface_hub import InferenceClient
    except ImportError as exc:
        raise RuntimeError(
            "huggingface_hub is not installed. Run: pip install -r requirements.txt"
        ) from exc

    # Hugging Face automatically routes to an available inference provider.
    # FLUX.1-schnell is designed for a small number of denoising steps.
    client = InferenceClient(api_key=settings.hf_api_key)

    return client.text_to_image(
        prompt=prompt,
        model=settings.image_model_id,
        width=settings.image_width,
        height=settings.image_height,
        num_inference_steps=settings.image_steps,
    )


def generate_image(image_prompt: str, panel_number: int) -> str:
    settings = get_settings()
    settings.ensure_directories()

    full_prompt = (
        f"{image_prompt}. "
        "Cinematic comic panel composition, strong storytelling silhouette, "
        "clear foreground and background separation, expressive characters, "
        "high visual clarity, no readable text, no speech bubbles."
    )

    try:
        if settings.image_backend.lower() != "hf":
            raise RuntimeError(
                "This fast build uses the Hugging Face remote image backend. "
                "Set IMAGE_BACKEND=hf in .env."
            )
        image = _hf_image(full_prompt)
    except Exception as exc:
        if not settings.dev_fallback:
            raise
        return _save_fallback_image(image_prompt, panel_number, str(exc))

    output = settings.panels_dir / safe_filename(f"panel_{panel_number}")
    image.save(output, format="PNG", optimize=True)
    return str(output)


def _save_fallback_image(image_prompt: str, panel_number: int, reason: str) -> str:
    settings = get_settings()
    image = Image.new("RGB", (settings.image_width, settings.image_height), (29, 36, 52))
    draw = ImageDraw.Draw(image)
    draw.rectangle(
        (18, 18, settings.image_width - 18, settings.image_height - 18),
        outline=(238, 190, 90), width=4,
    )
    draw.text((40, 40), f"COMIC PANEL {panel_number}", fill=(238, 190, 90))
    draw.text(
        (40, 90), shorten(image_prompt, width=90, placeholder="..."), fill=(240, 240, 240)
    )
    draw.text(
        (40, settings.image_height - 70),
        "Image generation unavailable; fallback panel used.",
        fill=(190, 200, 215),
    )
    output = settings.panels_dir / safe_filename(f"panel_{panel_number}")
    image.save(output, format="PNG")
    return str(output)

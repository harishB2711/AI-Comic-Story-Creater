from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

from app.config import BASE_DIR, get_settings
from app.schemas import PromptRequest
from app.services.gemini_flash import generate_comic_content
from app.services.image_generator import generate_image
from app.services.layout_builder import build_comic_layout
from app.services.exporters import save_pdf

router = APIRouter()
templates = Jinja2Templates(directory=BASE_DIR / "templates")


def _generate_images_fast(outline):
    """Generate remote images concurrently while preserving panel order."""
    panels = outline.panels
    settings = get_settings()
    # Fast mode sends all panels concurrently. This is much faster than
    # waiting for each remote image request to finish before starting the next.
    workers = len(panels)
    results = [None] * len(panels)

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {
            executor.submit(generate_image, panel.image_prompt, panel.panel_number): i
            for i, panel in enumerate(panels)
        }
        for future in futures:
            results[futures[future]] = future.result()
    return results


def _generate(request: PromptRequest):
    # One Gemini call instead of the old outline call + story call.
    outline, story = generate_comic_content(
        request.story_prompt,
        request.character_name,
        request.setting,
        request.tone,
        request.art_style,
    )

    # Remote image generation in parallel instead of local Stable Diffusion
    # running sequentially on the user's machine.
    image_paths = _generate_images_fast(outline)

    layout = build_comic_layout(outline, story, image_paths)
    title = f"{request.character_name}: {outline.panels[0].title}"
    pdf_path = save_pdf(title, layout)
    return title, layout, pdf_path


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={"error": None})


@router.post("/generate", response_class=HTMLResponse)
async def generate(
    request: Request,
    story_prompt: str = Form(...),
    character_name: str = Form(...),
    setting: str = Form(...),
    tone: str = Form(...),
    art_style: str = Form(...),
):
    try:
        data = PromptRequest(
            story_prompt=story_prompt,
            character_name=character_name,
            setting=setting,
            tone=tone,
            art_style=art_style,
        )
        title, layout, pdf_path = _generate(data)
        filename = Path(pdf_path).name
        return templates.TemplateResponse(
            request=request,
            name="comic_preview.html",
            context={
                "title": title,
                "layout": [p.model_dump() for p in layout],
                "pdf_url": f"/download/{filename}",
            },
        )
    except Exception as exc:
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={"error": str(exc)},
            status_code=500,
        )


@router.post("/generate-comic/json")
async def generate_json(payload: PromptRequest):
    try:
        title, layout, pdf_path = _generate(payload)
        return {
            "title": title,
            "panels": [p.model_dump() for p in layout],
            "pdf_url": f"/download/{Path(pdf_path).name}",
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/export-success", response_class=HTMLResponse)
async def export_success(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="export_success.html",
        context={"message": "Your comic PDF is ready."},
    )


@router.get("/download/{filename}")
async def download_pdf(filename: str):
    settings = get_settings()
    safe_name = Path(filename).name
    path = settings.exports_dir / safe_name
    if not path.exists() or path.suffix.lower() != ".pdf":
        raise HTTPException(status_code=404, detail="PDF not found.")
    return FileResponse(path=str(path), media_type="application/pdf", filename=safe_name)


@router.post("/test-image")
async def test_image(prompt: str = Form(...)):
    if len(prompt.strip()) < 3 or len(prompt) > 2000:
        raise HTTPException(status_code=422, detail="Prompt must be 3-2000 characters.")
    try:
        path = generate_image(prompt.strip(), 0)
        return {"image_url": f"/static/panels/{Path(path).name}"}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/health")
async def health():
    settings = get_settings()
    return {
        "status": "ok",
        "gemini_configured": settings.gemini_configured,
        "huggingface_token_configured": settings.hf_configured,
        "image_backend": settings.image_backend,
        "image_model": settings.image_model_id,
        "image_steps": settings.image_steps,
        "image_size": f"{settings.image_width}x{settings.image_height}",
        "panels": settings.effective_panels,
        "outline_model": settings.gemini_outline_model,
        "story_model": settings.gemini_story_model,
    }

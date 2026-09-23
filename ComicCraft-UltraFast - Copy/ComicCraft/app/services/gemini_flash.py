from google import genai
from pydantic import BaseModel, Field

from app.config import get_settings
from app.schemas import ComicOutline, ComicStory, PanelOutline, PanelStory
from app.services.gemini_client import generate_content_with_fallback


class GeneratedPanel(BaseModel):
    panel_number: int = Field(ge=1)
    title: str
    scene_description: str
    image_prompt: str
    caption: str
    narration: str
    dialogue: str = ""


class ComicGenerationResponse(BaseModel):
    panels: list[GeneratedPanel] = Field(min_length=1)


def _client() -> genai.Client:
    settings = get_settings()
    if not settings.gemini_api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured.")
    return genai.Client(api_key=settings.gemini_api_key)


def generate_comic_content(
    story_prompt: str,
    character_name: str,
    setting: str,
    tone: str,
    art_style: str,
) -> tuple[ComicOutline, ComicStory]:
    """Generate outline + comic copy in ONE Gemini request."""
    settings = get_settings()
    client = _client()

    prompt = f"""
You are the complete story director for ComicCraft.
Create exactly {settings.effective_panels} sequential comic panels.
Return ONLY the structured JSON object requested by the schema.

USER STORY IDEA:
{story_prompt}

MAIN CHARACTER:
{character_name}

SETTING:
{setting}

TONE:
{tone}

ART STYLE:
{art_style}

For every panel provide:
- panel_number: 1 through {settings.effective_panels}
- title: concise panel title
- scene_description: what the reader sees, including action and environment
- image_prompt: detailed text-to-image prompt; include the requested art style; do NOT include dialogue or readable text
- caption: short cinematic caption
- narration: 1-2 concise sentences
- dialogue: short character speech, or an empty string

Keep the same character identity, clothing, age, colors, and visual traits across panels.
Make the story have a beginning, development, turning point, and ending.
Keep image prompts visually clear and suitable for a text-to-image model.
"""

    response = generate_content_with_fallback(
        lambda model: client.models.generate_content(
            model=model,
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": ComicGenerationResponse,
            },
        ),
        [
            settings.gemini_story_model,
            settings.gemini_outline_model,
            "gemini-3.8-flash",
            "gemini-3.7-flash",
            "gemini-3.6-flash",
            "gemini-3.5-flash-lite",
        ],
    )

    if not response.parsed:
        raise RuntimeError("Gemini returned no structured comic content.")

    generated = response.parsed
    if len(generated.panels) != settings.effective_panels:
        raise RuntimeError(
            f"Gemini returned {len(generated.panels)} panels; expected {settings.effective_panels}."
        )

    outline = ComicOutline(
        panels=[
            PanelOutline(
                panel_number=p.panel_number,
                title=p.title,
                scene_description=p.scene_description,
                image_prompt=p.image_prompt,
            )
            for p in generated.panels
        ]
    )
    story = ComicStory(
        panels=[
            PanelStory(
                panel_number=p.panel_number,
                caption=p.caption,
                narration=p.narration,
                dialogue=p.dialogue,
            )
            for p in generated.panels
        ]
    )
    return outline, story


# Kept for compatibility with older code.
def generate_outline(story_prompt, character_name, setting, tone, art_style):
    outline, _ = generate_comic_content(
        story_prompt, character_name, setting, tone, art_style
    )
    return outline

from pydantic import BaseModel, Field, field_validator
from typing import List

class PromptRequest(BaseModel):
    story_prompt: str = Field(min_length=3, max_length=2000)
    character_name: str = Field(min_length=1, max_length=80)
    setting: str = Field(min_length=1, max_length=120)
    tone: str = Field(min_length=1, max_length=80)
    art_style: str = Field(min_length=1, max_length=120)

    @field_validator("*")
    @classmethod
    def strip_values(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Value cannot be empty.")
        return value

class PanelOutline(BaseModel):
    panel_number: int = Field(ge=1)
    title: str
    scene_description: str
    image_prompt: str

class ComicOutline(BaseModel):
    panels: List[PanelOutline]

class PanelStory(BaseModel):
    panel_number: int = Field(ge=1)
    caption: str
    narration: str
    dialogue: str

class ComicStory(BaseModel):
    panels: List[PanelStory]

class ComicPanel(BaseModel):
    panel_number: int
    title: str
    scene_description: str
    image_prompt: str
    image_url: str
    caption: str
    narration: str
    dialogue: str

class ComicResponse(BaseModel):
    title: str
    panels: List[ComicPanel]
    pdf_url: str | None = None

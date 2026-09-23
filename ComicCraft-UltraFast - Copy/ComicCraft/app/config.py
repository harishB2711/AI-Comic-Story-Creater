from functools import lru_cache
from pathlib import Path
from pydantic import Field, AliasChoices
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    gemini_api_key: str = Field(default="", validation_alias=AliasChoices("GEMINI_API_KEY"))
    gemini_outline_model: str = Field(
        default="gemini-3.8-flash",
        validation_alias=AliasChoices("GEMINI_OUTLINE_MODEL"),
    )
    gemini_story_model: str = Field(
        default="gemini-3.8-flash",
        validation_alias=AliasChoices("GEMINI_STORY_MODEL"),
    )

    # The uploaded project already uses HF_TOKEN in .env. Support the older
    # HF_API_KEY name too, so either setup works.
    hf_api_key: str = Field(
        default="",
        validation_alias=AliasChoices("HF_TOKEN", "HF_API_KEY"),
    )

    # Remote Hugging Face image generation is the fast path. It avoids loading
    # Stable Diffusion/FLUX weights into the user's PC RAM/VRAM.
    image_backend: str = Field(
        default="hf",
        validation_alias=AliasChoices("IMAGE_BACKEND"),
    )
    image_model_id: str = Field(
        default="black-forest-labs/FLUX.1-schnell",
        validation_alias=AliasChoices("HF_IMAGE_MODEL", "IMAGE_MODEL_ID"),
    )
    image_steps: int = Field(default=4, validation_alias=AliasChoices("IMAGE_STEPS"), ge=1, le=20)
    image_guidance: float = Field(default=0.0, validation_alias=AliasChoices("IMAGE_GUIDANCE"), ge=0, le=20)
    image_width: int = Field(default=512, validation_alias=AliasChoices("IMAGE_WIDTH"), ge=256, le=1536)
    image_height: int = Field(default=384, validation_alias=AliasChoices("IMAGE_HEIGHT"), ge=256, le=1536)
    image_device: str = Field(default="auto", validation_alias=AliasChoices("IMAGE_DEVICE"))
    dev_fallback: bool = Field(default=False, validation_alias=AliasChoices("DEV_FALLBACK"))
    fast_mode: bool = Field(default=True, validation_alias=AliasChoices("FAST_MODE"))

    app_host: str = Field(default="127.0.0.1", validation_alias=AliasChoices("APP_HOST"))
    app_port: int = Field(default=8000, validation_alias=AliasChoices("APP_PORT"))
    max_panels: int = Field(
        default=5,
        validation_alias=AliasChoices("PANELS_PER_COMIC", "MAX_PANELS"),
        ge=1,
        le=10,
    )

    panels_dir: Path = BASE_DIR / "static" / "panels"
    exports_dir: Path = BASE_DIR / "static" / "exports"

    @property
    def effective_panels(self) -> int:
        """Use fewer panels in Fast Mode even if an older .env asks for 5+."""
        return min(self.max_panels, 4) if self.fast_mode else self.max_panels

    def ensure_directories(self) -> None:
        self.panels_dir.mkdir(parents=True, exist_ok=True)
        self.exports_dir.mkdir(parents=True, exist_ok=True)

    @property
    def gemini_configured(self) -> bool:
        return bool(self.gemini_api_key)

    @property
    def hf_configured(self) -> bool:
        return bool(self.hf_api_key)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    settings = Settings()
    settings.ensure_directories()
    return settings

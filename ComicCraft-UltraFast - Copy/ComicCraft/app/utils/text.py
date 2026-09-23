import re
from pathlib import Path
from uuid import uuid4

def safe_filename(value: str, suffix: str = ".png") -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_-]+", "_", value).strip("_")
    cleaned = cleaned[:60] or "panel"
    return f"{cleaned}_{uuid4().hex[:10]}{suffix}"

def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()

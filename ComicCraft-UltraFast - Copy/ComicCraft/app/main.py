from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import BASE_DIR
from app.routes import router

app = FastAPI(
    title="ComicCraft",
    description="Fast AI Comic Story Creator using Gemini and Hugging Face Inference Providers",
    version="2.0.0",
)

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
app.include_router(router)

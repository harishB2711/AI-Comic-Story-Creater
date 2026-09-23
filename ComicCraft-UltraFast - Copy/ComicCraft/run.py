import uvicorn
from pathlib import Path

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        app_dir=str(Path(__file__).resolve().parent),
        host="127.0.0.1",
        port=8000,
        reload=True,
    )

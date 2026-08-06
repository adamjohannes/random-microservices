import uvicorn

from src.course.adapters.driving.http.app import create_app
from src.course.config import Config

app = create_app()

if __name__ == "__main__":
    cfg = Config()
    uvicorn.run("main:app", host="0.0.0.0", port=cfg.port, reload=cfg.environment == "development")

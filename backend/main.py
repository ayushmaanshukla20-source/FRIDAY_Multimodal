from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.core.config import settings
from backend.core.database import init_db
from backend.core.logging import logger

# Import API Routers
from backend.api.health import router as health_router
from backend.api.chat import router as chat_router
from backend.api.documents import router as documents_router
from backend.api.knowledge import router as knowledge_router
from backend.api.models import router as models_router
from backend.api.multimodal import router as multimodal_router
from backend.api.audio import router as audio_router
from backend.api.images import router as images_router
from backend.api.viewer import router as viewer_router
from backend.api.desktop import router as desktop_router
from backend.api.spotify import router as spotify_router
from backend.api.music import router as music_router
from backend.api.chrome_api import router as chrome_router
from backend.api.study_api import router as study_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup sequence
    logger.info("Initializing F.R.I.D.A.Y. System Architecture...")
    db_ok = init_db()
    if db_ok:
        logger.info("MySQL Database operational and synchronized.")
    else:
        logger.warning("MySQL connection deferred or unavailable. Health endpoint reports remediation details.")
    yield
    # Shutdown sequence
    logger.info("Shutting down F.R.I.D.A.Y. Operational Core.")

app = FastAPI(
    title="F.R.I.D.A.Y. Operational Backend",
    description="Multimodal AI Assistant with 3D Holographic Interface, RAG, and Desktop Automation",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware
origins = settings.parsed_allowed_origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global safe exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled operational exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "Boss, an internal operational exception occurred. Core subsystems remain shielded.",
            "detail": str(exc) if settings.app_env == "development" else "Internal server exception."
        }
    )

# Include Routers
app.include_router(health_router)
app.include_router(chat_router)
app.include_router(documents_router)
app.include_router(knowledge_router)
app.include_router(models_router)
app.include_router(multimodal_router)
app.include_router(audio_router)
app.include_router(images_router)
app.include_router(viewer_router)
app.include_router(desktop_router)
app.include_router(spotify_router)
app.include_router(music_router)
app.include_router(chrome_router)
app.include_router(study_router)

# Root-level backward compatibility route
@app.post("/chat")
def legacy_chat(request: dict):
    from backend.api.chat import chat_endpoint
    from backend.schemas.chat import ChatRequest
    prompt = request.get("prompt", "")
    req = ChatRequest(prompt=prompt, use_rag=False)
    res = chat_endpoint(req)
    return {"response": res.response}


@app.get("/")
def root():
    return {
        "system": "F.R.I.D.A.Y.",
        "status": "online",
        "protocol": "HTTP/1.1 REST API",
        "docs_url": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host=settings.app_host, port=settings.app_port, reload=True)

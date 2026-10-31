from fastapi import APIRouter
from backend.core.config import settings
from backend.schemas.models import ModelListResponse, ModelInfo
from backend.services.ai_service import ai_service

router = APIRouter(prefix="/api/models", tags=["Model Telemetry"])

@router.get("", response_model=ModelListResponse)
def get_supported_models():
    """
    Returns the catalog of configured and available multimodal AI models.
    """
    has_key = ai_service.is_configured()
    
    models = [
        ModelInfo(
            id="gemini-1.5-flash",
            name="Google Gemini 1.5 Flash (Multimodal & Fast)",
            provider="Google GenAI",
            type="chat/vision",
            is_active=settings.llm_model_name == "gemini-1.5-flash" and has_key
        ),
        ModelInfo(
            id="gemini-1.5-pro",
            name="Google Gemini 1.5 Pro (Deep Reasoning)",
            provider="Google GenAI",
            type="chat/vision",
            is_active=settings.llm_model_name == "gemini-1.5-pro" and has_key
        ),
        ModelInfo(
            id="text-embedding-004",
            name="Text Embedding 004",
            provider="Google GenAI",
            type="embedding",
            is_active=settings.embedding_model_name == "text-embedding-004" and has_key
        ),
        ModelInfo(
            id="imagen-3.0-generate-002",
            name="Google Imagen 3 (High-Fidelity Visual Synthesis)",
            provider="Google GenAI",
            type="image",
            is_active=has_key
        ),
        ModelInfo(
            id="ollama-local",
            name="Ollama Local Engine (Offline Inference)",
            provider="Ollama",
            type="chat",
            is_active=settings.llm_provider.lower() == "ollama"
        )
    ]

    return ModelListResponse(
        models=models,
        active_llm=settings.llm_model_name,
        active_embedding=settings.embedding_model_name,
        active_vision=settings.vision_model_name
    )

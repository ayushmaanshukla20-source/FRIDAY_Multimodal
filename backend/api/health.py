from fastapi import APIRouter
from backend.core.config import settings
from backend.core.database import get_db_status
from backend.services.ai_service import ai_service
from backend.services.rag_service import rag_service
from backend.integrations.desktop_control import desktop_control

router = APIRouter(prefix="/api", tags=["Health & Diagnostics"])

@router.get("/health")
def health_check():
    """
    Comprehensive system health and subsystem status check.
    Returns status of Database, Vector Store, AI Provider, and System Telemetry.
    """
    db_status = get_db_status()
    system_info = desktop_control.get_system_diagnostics()
    
    vector_count = 0
    vector_status = "operational"
    try:
        if rag_service._collection:
            vector_count = rag_service._collection.count()
        else:
            vector_status = "degraded"
    except Exception as e:
        vector_status = f"error: {str(e)}"

    return {
        "status": "healthy" if db_status["connected"] else "degraded",
        "system_name": "F.R.I.D.A.Y. Operational Core",
        "version": "1.0.0",
        "database": db_status,
        "vector_store": {
            "status": vector_status,
            "collection": rag_service.collection_name,
            "total_vectors": vector_count,
            "engine": "ChromaDB"
        },
        "ai_provider": {
            "provider": settings.llm_provider,
            "model": settings.llm_model_name,
            "is_configured": ai_service.is_configured(),
            "has_api_key": bool(settings.effective_api_key)
        },
        "integrations": {
            "desktop_control": settings.desktop_control_enabled,
            "spotify_configured": True,
            "music_streaming": True
        },
        "telemetry": system_info
    }

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
from backend.core.config import settings
from backend.schemas.models import ImageGenerateRequest, ImageGenerateResponse
from backend.services.image_service import image_service

router = APIRouter(prefix="/api/images", tags=["Image Generation"])

@router.post("/generate", response_model=ImageGenerateResponse)
def generate_image(request: ImageGenerateRequest):
    """
    Generates synthetic imagery from a text prompt.
    """
    res = image_service.generate_image(
        prompt=request.prompt,
        aspect_ratio=request.aspect_ratio
    )
    return ImageGenerateResponse(
        image_url=res.get("image_url"),
        image_base64=res.get("image_base64"),
        prompt=request.prompt,
        success=res.get("success", False),
        message=res.get("message", "Image generation executed.")
    )

@router.get("/view/{filename}")
def view_image(filename: str):
    """
    Serves a generated image file.
    """
    safe_name = Path(filename).name
    filepath = Path(settings.generated_dir) / safe_name
    if not filepath.is_file():
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(
        path=str(filepath),
        media_type="image/jpeg",
        filename=safe_name,
        headers={"Content-Disposition": f'inline; filename="{safe_name}"'}
    )

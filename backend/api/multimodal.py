from fastapi import APIRouter
from backend.schemas.models import MultimodalAnalyseRequest, MultimodalAnalyseResponse
from backend.services.multimodal_service import multimodal_service

router = APIRouter(prefix="/api/multimodal", tags=["Multimodal Analysis"])

@router.post("/analyse", response_model=MultimodalAnalyseResponse)
def analyse_input(request: MultimodalAnalyseRequest):
    """
    Performs multimodal vision analysis on images, diagrams, handwritten notes, or equations.
    """
    result = multimodal_service.analyze_image(
        prompt=request.prompt or "Analyze this visual input, Boss.",
        image_base64=request.image_base64,
        task_type=request.analysis_type or "general"
    )

    return MultimodalAnalyseResponse(
        analysis=result.get("analysis", "Analysis complete, Boss."),
        modality="image",
        status=result.get("status", "success"),
        extracted_text=result.get("extracted_text")
    )

@router.post("/ocr", response_model=MultimodalAnalyseResponse)
def ocr_notes(request: MultimodalAnalyseRequest):
    """Convenience endpoint: Handwritten notes to clean digital Markdown notes."""
    result = multimodal_service.analyze_image(
        prompt=request.prompt or "Transcribe these handwritten notes into structured Markdown notes.",
        image_base64=request.image_base64,
        task_type="ocr_notes"
    )
    return MultimodalAnalyseResponse(
        analysis=result.get("analysis", "Transcribed notes."),
        modality="image",
        status=result.get("status", "success")
    )

@router.post("/diagram", response_model=MultimodalAnalyseResponse)
def analyze_diagram(request: MultimodalAnalyseRequest):
    """Convenience endpoint: Deconstruct science/flowchart diagrams and produce Mermaid.js."""
    result = multimodal_service.analyze_image(
        prompt=request.prompt or "Deconstruct this diagram and provide a Mermaid.js flowchart.",
        image_base64=request.image_base64,
        task_type="analyze_diagram"
    )
    return MultimodalAnalyseResponse(
        analysis=result.get("analysis", "Diagram analysis complete."),
        modality="image",
        status=result.get("status", "success")
    )

@router.post("/solve", response_model=MultimodalAnalyseResponse)
def solve_problem(request: MultimodalAnalyseRequest):
    """Convenience endpoint: Step-by-step problem solver with LaTeX math."""
    result = multimodal_service.analyze_image(
        prompt=request.prompt or "Solve this problem step-by-step with LaTeX equations.",
        image_base64=request.image_base64,
        task_type="solve_problem"
    )
    return MultimodalAnalyseResponse(
        analysis=result.get("analysis", "Problem solved."),
        modality="image",
        status=result.get("status", "success")
    )

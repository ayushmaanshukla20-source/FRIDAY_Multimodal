from fastapi import APIRouter
from backend.schemas.models import ViewerCommandRequest, ViewerCommandResponse, ViewerAction
from backend.services.viewer_service import viewer_service

router = APIRouter(prefix="/api/viewer", tags=["3D Holographic Viewer"])

@router.post("/command", response_model=ViewerCommandResponse)
def execute_viewer_command(request: ViewerCommandRequest):
    """
    Parses and translates natural-language viewport instructions into structured Three.js viewer actions.
    """
    parsed, actions_list, message = viewer_service.parse_command(request.command)
    actions = [ViewerAction(**a) for a in actions_list]

    return ViewerCommandResponse(
        parsed=parsed,
        command=request.command,
        actions=actions,
        message=message
    )

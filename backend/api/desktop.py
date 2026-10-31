from fastapi import APIRouter
from backend.schemas.models import DesktopExecuteRequest, DesktopExecuteResponse
from backend.integrations.desktop_control import desktop_control
from backend.integrations.screen_analysis import screen_analysis

router = APIRouter(prefix="/api/desktop", tags=["Desktop Automation & Vision"])

@router.post("/execute", response_model=DesktopExecuteResponse)
def execute_desktop_action(request: DesktopExecuteRequest):
    """
    Executes an allowlisted desktop tool, application launch, or system diagnosis.
    """
    res = desktop_control.execute_action(
        action=request.action,
        target=request.target,
        confirmed=request.confirmed
    )

    return DesktopExecuteResponse(
        success=res["success"],
        action=res["action"],
        target=res["target"],
        output=res["output"],
        requires_confirmation=res["requires_confirmation"]
    )

@router.post("/screen/capture")
def capture_and_analyze_screen(prompt: str = "Analyze this screen capture, Boss."):
    """
    Captures the primary desktop screen and analyzes its visible content with vision AI.
    """
    return screen_analysis.analyze_current_screen(prompt=prompt)

@router.get("/mcp/status")
def get_chrome_mcp_status():
    """
    Returns Chrome DevTools MCP server status and available tools.
    """
    from backend.integrations.chrome_mcp import chrome_mcp_client
    return chrome_mcp_client.get_status()

@router.post("/mcp/navigate")
def chrome_mcp_navigate(url: str):
    """
    Navigates Chrome to target URL using the Chrome DevTools MCP server.
    """
    from backend.integrations.chrome_mcp import chrome_mcp_client
    return chrome_mcp_client.navigate(url)

@router.post("/mcp/screenshot")
def chrome_mcp_screenshot():
    """
    Captures active page screenshot via Chrome DevTools MCP server.
    """
    from backend.integrations.chrome_mcp import chrome_mcp_client
    return chrome_mcp_client.take_screenshot()


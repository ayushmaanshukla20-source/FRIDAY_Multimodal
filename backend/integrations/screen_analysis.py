import io
import base64
from typing import Dict, Any, Optional
from PIL import ImageGrab
from backend.core.logging import logger
from backend.services.multimodal_service import multimodal_service

class ScreenAnalysisIntegration:
    @staticmethod
    def capture_screen() -> Optional[bytes]:
        """
        Captures the primary desktop screen using PIL.ImageGrab.
        Safe, local operation on Windows.
        """
        try:
            screenshot = ImageGrab.grab()
            buffer = io.BytesIO()
            screenshot.save(buffer, format="PNG")
            return buffer.getvalue()
        except Exception as e:
            logger.error(f"Failed to capture desktop screen: {e}")
            return None

    def analyze_current_screen(self, prompt: Optional[str] = None) -> Dict[str, Any]:
        """
        Captures active screen with permission and passes it to multimodal service.
        """
        screen_bytes = self.capture_screen()
        if not screen_bytes:
            return {
                "success": False,
                "analysis": "Boss, unable to acquire screen capture. Ensure desktop capture permissions are enabled.",
                "image_base64": None
            }

        b64_screen = base64.b64encode(screen_bytes).decode("utf-8")
        analysis_prompt = prompt or "Analyze what is currently open on my screen, identify any errors or active work, and summarize it, Boss."
        
        result = multimodal_service.analyze_image(
            prompt=analysis_prompt,
            image_bytes=screen_bytes,
            mime_type="image/png"
        )

        return {
            "success": True,
            "analysis": result.get("analysis", "Screen captured successfully."),
            "metadata": result.get("metadata", {}),
            "image_base64": f"data:image/png;base64,{b64_screen}"
        }

screen_analysis = ScreenAnalysisIntegration()

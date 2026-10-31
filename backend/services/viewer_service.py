import re
from typing import List, Dict, Any, Tuple
from backend.core.logging import logger

class ViewerService:
    @staticmethod
    def parse_command(command: str) -> Tuple[bool, List[Dict[str, Any]], str]:
        """
        Parses natural language 3D viewer commands into validated structured actions.
        """
        cmd = command.strip().lower()
        actions: List[Dict[str, Any]] = []

        # 1. Wireframe commands
        if "wireframe" in cmd:
            if any(w in cmd for w in ["disable", "off", "solid", "hide", "deactivate"]):
                actions.append({"action": "wireframe", "params": {"enabled": False}})
                msg = "Right away, Boss. Disabling wireframe mode."
            elif any(w in cmd for w in ["enable", "on", "show", "activate"]):
                actions.append({"action": "wireframe", "params": {"enabled": True}})
                msg = "Right away, Boss. Wireframe holographic grid enabled."
            else:
                actions.append({"action": "wireframe", "params": {"toggle": True}})
                msg = "Right away, Boss. Toggling wireframe display."
            return True, actions, msg

        # 2. Rotation commands
        if "rotate" in cmd or "turn" in cmd or "spin" in cmd:
            # Extract degrees if specified (avoid matching '3d')
            deg_match = re.search(r"(\d+)\s*(?:deg|degree|degrees)\b", cmd)
            if not deg_match:
                # Look for numbers not immediately followed by 'd'
                deg_match = re.search(r"\b(\d+)\b(?!d)", cmd)
            degrees = int(deg_match.group(1)) if deg_match else 45
            
            # Detect axis
            axis = "y"
            if "x-axis" in cmd or "x axis" in cmd or "pitch" in cmd:
                axis = "x"
            elif "z-axis" in cmd or "z axis" in cmd or "roll" in cmd:
                axis = "z"

            # Detect direction
            if "left" in cmd or "counter" in cmd or "negative" in cmd:
                degrees = -abs(degrees)

            # Continuous spin vs step
            if "continuous" in cmd or "start spinning" in cmd or "auto" in cmd:
                actions.append({"action": "auto_rotate", "params": {"enabled": True}})
                msg = "Right away, Boss. Holographic continuous auto-rotation engaged."
            elif "stop" in cmd:
                actions.append({"action": "auto_rotate", "params": {"enabled": False}})
                msg = "Right away, Boss. Auto-rotation halted."
            else:
                actions.append({"action": "rotate", "params": {"axis": axis, "degrees": degrees}})
                msg = f"Right away, Boss. Rotating model {degrees}° along the {axis.upper()}-axis."
            return True, actions, msg

        # 3. Zoom commands
        if "zoom" in cmd or "closer" in cmd or "further" in cmd or "magnify" in cmd:
            if any(w in cmd for w in ["out", "further", "back", "decrease"]):
                actions.append({"action": "zoom", "params": {"factor": 1.3}})
                msg = "Right away, Boss. Pulling back holographic camera."
            else:
                actions.append({"action": "zoom", "params": {"factor": 0.75}})
                msg = "Right away, Boss. Zooming in optical sensors."
            return True, actions, msg

        # 4. Reset view commands
        if any(w in cmd for w in ["reset", "center", "recenter", "default view", "home"]):
            actions.append({"action": "reset", "params": {}})
            return True, actions, "Right away, Boss. Holographic projection coordinates reset to origin."

        # 5. Component Hierarchy commands
        if any(w in cmd for w in ["hierarchy", "components", "tree", "parts", "layers"]):
            actions.append({"action": "hierarchy", "params": {}})
            return True, actions, "Analysis complete, Boss. Expanding component structural hierarchy."

        # 6. Grid / HUD commands
        if "grid" in cmd:
            toggle = False if ("hide" in cmd or "off" in cmd or "disable" in cmd) else True
            actions.append({"action": "grid", "params": {"enabled": toggle}})
            return True, actions, f"Right away, Boss. Holographic spatial grid {'enabled' if toggle else 'disabled'}."

        # 7. Procedural geometry generation
        if any(w in cmd for w in ["project", "generate", "create", "load", "model", "render"]):
            model_type = "reactor"
            if "satellite" in cmd or "probe" in cmd:
                model_type = "satellite"
            elif "torus" in cmd or "ring" in cmd:
                model_type = "torus"
            elif "cube" in cmd or "tesseract" in cmd:
                model_type = "cube"
            elif "core" in cmd or "reactor" in cmd:
                model_type = "reactor"

            actions.append({"action": "procedural", "params": {"type": model_type}})
            return True, actions, f"Right away, Boss. Projecting 3D holographic {model_type} assembly."

        # Default fallback
        actions.append({"action": "inspect", "params": {"raw_command": command}})
        return False, actions, f"Boss, received 3D telemetry command: '{command}'. Stand by for standard viewport response."

viewer_service = ViewerService()

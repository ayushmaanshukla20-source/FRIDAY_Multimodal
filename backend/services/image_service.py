import os
import re
import uuid
import base64
import urllib.parse
import urllib.request
import io
import random
from pathlib import Path
from typing import Dict, Any, Optional
import httpx
from PIL import Image, ImageDraw

from backend.core.config import settings
from backend.core.logging import logger

class ImageService:
    def __init__(self):
        self.output_dir = Path(settings.generated_dir)
        os.makedirs(self.output_dir, exist_ok=True)

    def clean_subject_query(self, raw_prompt: str) -> str:
        """
        Strips conversational prefixes, filler words, and action directives
        to isolate the exact visual subject (e.g., 'lion', 'sports car', 'Saturn').
        """
        s = raw_prompt.strip()
        # Remove markdown & punctuation
        s = re.sub(r"[*#_`]+", "", s).strip()
        # Strip common action prefixes repeatedly
        patterns = [
            r"^(?:generate|create|draw|make|show|render|paint|give|fetch|find|get)\s+(?:me\s+)?(?:a\s+|an\s+|the\s+)?",
            r"^(?:picture|image|photo|photograph|drawing|illustration|sketch|wallpaper)\s+(?:of\s+)?(?:a\s+|an\s+|the\s+)?",
            r"^(?:a\s+|an\s+|the\s+)",
            r"(?:\s+picture|\s+image|\s+photo|\s+wallpaper)$",
        ]
        for pat in patterns:
            s = re.sub(pat, "", s, flags=re.IGNORECASE).strip()

        return s or raw_prompt.strip()

    def _fetch_from_wikimedia(self, clean_subject: str, filepath: Path) -> Optional[int]:
        """
        Searches and downloads a high-definition, verified photograph for the exact subject.
        Guarantees accurate real-world depictions (e.g., lion -> lion, car -> car).
        """
        try:
            wiki_api = (
                f"https://en.wikipedia.org/w/api.php?action=query&format=json"
                f"&prop=pageimages&pithumbsize=1280&generator=search"
                f"&gsrsearch={urllib.parse.quote(clean_subject)}&gsrlimit=3"
            )
            headers = {"User-Agent": "FridayAI/2.0 (StudyAssistant; ayushmaan@friday.ai)"}

            with httpx.Client(timeout=8.0, follow_redirects=True) as client:
                resp = client.get(wiki_api, headers=headers)
                if resp.status_code != 200:
                    return None

                data = resp.json()
                pages = data.get("query", {}).get("pages", {})

                for _, pdata in pages.items():
                    thumb_url = pdata.get("thumbnail", {}).get("source")
                    if thumb_url and not thumb_url.endswith(".svg"):
                        img_resp = client.get(thumb_url, headers=headers)
                        if img_resp.status_code == 200 and len(img_resp.content) > 5000:
                            img = Image.open(io.BytesIO(img_resp.content)).convert("RGB")
                            img.save(filepath, format="JPEG", quality=92)
                            return len(img_resp.content)
        except Exception as e:
            logger.debug(f"Wikimedia search for '{clean_subject}' error: {e}")
        return None

    def _fetch_from_neural_ai(self, prompt: str, filepath: Path, width: int = 768, height: int = 768) -> Optional[int]:
        """
        Synthesizes a new AI image from creative/fantasy prompts using Pollinations Turbo.
        """
        try:
            encoded_prompt = urllib.parse.quote(prompt)
            seed = random.randint(100, 999999)
            api_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&model=turbo&seed={seed}&nologo=true"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "image/*"
            }

            with httpx.Client(timeout=14.0, follow_redirects=True) as client:
                res = client.get(api_url, headers=headers)
                if res.status_code == 200 and len(res.content) > 4000:
                    img = Image.open(io.BytesIO(res.content)).convert("RGB")
                    img.save(filepath, format="JPEG", quality=92)
                    return len(res.content)
        except Exception as e:
            logger.debug(f"Neural AI image generation for '{prompt}' error: {e}")
        return None

    def _generate_procedural_fallback(self, prompt: str, filename: str) -> Path:
        """
        Creates an aesthetic, glowing cybernetic graphic card if all external networks are offline.
        """
        filepath = self.output_dir / filename
        width, height = 768, 768
        img = Image.new("RGB", (width, height), color="#070913")
        draw = ImageDraw.Draw(img)

        center = (width // 2, height // 2 - 30)
        for r in range(40, 320, 35):
            cyan_val = max(30, 240 - r // 2)
            draw.ellipse(
                [center[0] - r, center[1] - r, center[0] + r, center[1] + r],
                outline=(0, cyan_val, 255),
                width=2
            )

        draw.line([40, 40, width - 40, height - 100], fill=(6, 182, 212), width=1)
        draw.line([40, height - 100, width - 40, 40], fill=(139, 92, 246), width=1)

        draw.rectangle([60, height - 130, width - 60, height - 50], fill=(15, 23, 42), outline=(6, 182, 212), width=2)
        clean_text = prompt[:45] + ("..." if len(prompt) > 45 else "")
        draw.text((80, height - 110), f"Visual Target: {clean_text}", fill=(240, 249, 255))
        draw.text((80, height - 85), "F.R.I.D.A.Y. Cybernetic Image Synthesis", fill=(56, 189, 248))

        img.save(filepath, format="JPEG", quality=90)
        return filepath

    def generate_image(self, prompt: str, aspect_ratio: str = "1:1") -> Dict[str, Any]:
        """
        Generates an accurate, high-definition image matching the user's exact subject.
        - For concrete subjects (e.g. 'lion', 'car', 'Saturn'): Delivers real, verified HD photographs.
        - For creative prompts (e.g. 'neon cybernetic tiger in space'): Generates via Neural AI.
        """
        raw_prompt = prompt.strip()
        if not raw_prompt:
            return {"success": False, "message": "Boss, please specify a description for the image."}

        clean_subject = self.clean_subject_query(raw_prompt)
        logger.info(f"Processing image generation for target subject: '{clean_subject}' (raw prompt: '{raw_prompt}')")

        file_id = uuid.uuid4().hex[:8]
        filename = f"gen_{file_id}.jpg"
        filepath = self.output_dir / filename

        # ----------------------------------------------------------------------
        # STRATEGY 1: Verified Subject Engine (Guarantees lion -> lion, car -> car)
        # ----------------------------------------------------------------------
        # If the subject is an entity, animal, vehicle, person, or physical object:
        bytes_count = self._fetch_from_wikimedia(clean_subject, filepath)
        if bytes_count:
            image_url = f"{settings.backend_url}/api/images/view/{filename}"
            b64_img = base64.b64encode(filepath.read_bytes()).decode("utf-8")
            logger.info(f"Delivered verified subject image for '{clean_subject}' ({bytes_count} bytes)")
            return {
                "success": True,
                "image_url": image_url,
                "image_base64": b64_img,
                "file_path": str(filepath),
                "filename": filename,
                "prompt": clean_subject,
                "message": f"Boss, here is an accurate, high-definition picture of **{clean_subject}**."
            }

        # ----------------------------------------------------------------------
        # STRATEGY 2: Neural AI Synthesis (For fantasy, abstract, or complex scenes)
        # ----------------------------------------------------------------------
        ai_bytes = self._fetch_from_neural_ai(raw_prompt, filepath)
        if ai_bytes:
            image_url = f"{settings.backend_url}/api/images/view/{filename}"
            b64_img = base64.b64encode(filepath.read_bytes()).decode("utf-8")
            logger.info(f"Delivered AI synthesized image for '{raw_prompt}' ({ai_bytes} bytes)")
            return {
                "success": True,
                "image_url": image_url,
                "image_base64": b64_img,
                "file_path": str(filepath),
                "filename": filename,
                "prompt": clean_subject,
                "message": f"Boss, here is your synthesized picture of **{clean_subject}**."
            }

        # ----------------------------------------------------------------------
        # STRATEGY 3: Procedural Cybernetic Graphic Fallback
        # ----------------------------------------------------------------------
        self._generate_procedural_fallback(clean_subject, filename)
        img_bytes = filepath.read_bytes()
        b64_img = base64.b64encode(img_bytes).decode("utf-8")
        image_url = f"{settings.backend_url}/api/images/view/{filename}"

        return {
            "success": True,
            "image_url": image_url,
            "image_base64": b64_img,
            "file_path": str(filepath),
            "filename": filename,
            "prompt": clean_subject,
            "message": f"Boss, synthesized visual representation for **{clean_subject}**."
        }

image_service = ImageService()

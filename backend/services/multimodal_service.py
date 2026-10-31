import io
import base64
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
from PIL import Image
from backend.core.config import settings
from backend.core.logging import logger
from backend.services.ai_service import ai_service, FRIDAY_SYSTEM_PROMPT

class MultimodalService:
    @staticmethod
    def inspect_image(image_bytes: bytes) -> Dict[str, Any]:
        """Validates and extracts technical metadata from image bytes using Pillow."""
        try:
            img = Image.open(io.BytesIO(image_bytes))
            return {
                "format": img.format or "Unknown",
                "width": img.width,
                "height": img.height,
                "mode": img.mode,
                "is_valid": True,
                "aspect_ratio": round(img.width / max(1, img.height), 2)
            }
        except Exception as e:
            logger.warning(f"Failed to inspect image: {e}")
            return {"is_valid": False, "error": str(e)}

    def analyze_image(
        self,
        prompt: str,
        image_bytes: Optional[bytes] = None,
        image_base64: Optional[str] = None,
        mime_type: str = "image/png",
        task_type: str = "general"
    ) -> Dict[str, Any]:
        """
        Analyzes an image using configured vision LLM with academic student productivity task support:
        - 'ocr_notes': Transcribe handwritten/printed notes into clean searchable Markdown
        - 'analyze_diagram': Deconstruct diagrams, explain mechanisms, output Mermaid chart
        - 'solve_problem': Step-by-step problem solver with LaTeX equations
        - 'generate_quiz': Produce practice flashcards and assessment questions
        - 'general': Complete multimodal feature inspection
        """
        # Resolve bytes
        if image_base64 and not image_bytes:
            if "," in image_base64:
                header, encoded = image_base64.split(",", 1)
                if "image/jpeg" in header or "image/jpg" in header:
                    mime_type = "image/jpeg"
                elif "image/webp" in header:
                    mime_type = "image/webp"
                elif "image/gif" in header:
                    mime_type = "image/gif"
                image_bytes = base64.b64decode(encoded)
            else:
                image_bytes = base64.b64decode(image_base64)

        if not image_bytes:
            return {
                "status": "error",
                "analysis": "Boss, no image data was provided for analysis.",
                "extracted_text": None
            }

        # Validate with PIL
        meta = self.inspect_image(image_bytes)
        if not meta.get("is_valid", False):
            return {
                "status": "error",
                "analysis": f"Boss, the visual payload appears corrupted or unsupported: {meta.get('error')}",
                "extracted_text": None
            }

        # Build academic task-oriented prompt
        constructed_prompt = prompt or ""
        if task_type == "ocr_notes":
            constructed_prompt = (
                f"{constructed_prompt}\n\n"
                "Task: You are performing high-precision Optical Character Recognition (OCR) on handwritten/textbook study notes.\n"
                "1. Transcribe all text accurately, preserving headings, bullet points, numbered lists, and formulas.\n"
                "2. Format equations in LaTeX ($...$ or $$...$$).\n"
                "3. Organize the transcription into clean, structured Markdown study notes.\n"
                "4. Add an '💡 Key Study Takeaways' section summarizing the core concepts."
            )
        elif task_type == "analyze_diagram":
            constructed_prompt = (
                f"{constructed_prompt}\n\n"
                "Task: You are analyzing a study diagram, chart, or scientific figure.\n"
                "1. Identify and label all key components, entities, pathways, or stages.\n"
                "2. Explain the fundamental mechanism, process, or logic represented.\n"
                "3. Generate a renderable Mermaid.js flowchart or concept map (```mermaid ... ```) reconstructing this visual structure.\n"
                "4. Highlight critical points frequently tested on exams."
            )
        elif task_type == "solve_problem":
            constructed_prompt = (
                f"{constructed_prompt}\n\n"
                "Task: You are solving a student homework problem, math equation, physics calculation, or debugging code.\n"
                "1. State the given information and what needs to be solved/proved.\n"
                "2. Provide a rigorous, step-by-step solution with explanations for each step.\n"
                "3. Use LaTeX math formatting ($...$ and $$...$$) for all formulas and calculations.\n"
                "4. Provide the final verified answer in a bold highlight box, along with common pitfalls to avoid."
            )
        elif task_type == "generate_quiz":
            constructed_prompt = (
                f"{constructed_prompt}\n\n"
                "Task: Based on the visual content of this image, generate a high-yield study assessment.\n"
                "1. Create 5 conceptual quiz questions (multiple choice or short answer).\n"
                "2. Provide detailed answers and explanations for self-assessment.\n"
                "3. List 3 high-priority flashcard concepts (Question -> Answer)."
            )
        elif not constructed_prompt:
            constructed_prompt = "Examine this academic study material in detail. Identify key concepts, extract text, and provide structured insights, Boss."

        # Check AI provider
        client = ai_service._get_genai_client()
        if client and ai_service.is_configured():
            try:
                from google.genai import types

                part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)

                candidate_models = [
                    settings.vision_model_name,
                    "gemini-3.1-flash-lite",
                    "gemini-3-flash-preview",
                    "gemini-flash-lite-latest",
                ]
                candidate_models = list(dict.fromkeys(candidate_models))

                last_err = None
                for model_id in candidate_models:
                    try:
                        response = client.models.generate_content(
                            model=model_id,
                            contents=[part, types.Part.from_text(text=constructed_prompt)],
                            config=types.GenerateContentConfig(
                                system_instruction=FRIDAY_SYSTEM_PROMPT,
                                temperature=0.3
                            )
                        )
                        return {
                            "status": "success",
                            "analysis": response.text or "Boss, visual analysis returned no descriptive tokens.",
                            "metadata": meta,
                            "task_type": task_type,
                            "extracted_text": None
                        }
                    except Exception as e:
                        last_err = e
                        logger.warning(f"Vision model {model_id} failed: {e}. Trying fallback...")
                        continue

                raise last_err or Exception("All vision models exhausted.")
            except Exception as e:
                logger.error(f"Multimodal vision generation failed: {e}")
                return {
                    "status": "partial",
                    "analysis": f"Boss, optical sensor connection reported an issue ({str(e)}). Structural telemetry: {meta['width']}x{meta['height']} {meta['format']} format ({meta['mode']} mode).",
                    "metadata": meta
                }

        # Fallback without external API
        return {
            "status": "success",
            "analysis": (
                f"Boss, visual payload received. Structural analysis:\n"
                f"- Dimensions: {meta['width']} x {meta['height']} px (Aspect Ratio: {meta['aspect_ratio']})\n"
                f"- Image Format: {meta['format']}\n"
                f"- Color Mode: {meta['mode']}\n\n"
                "Please configure your `GEMINI_API_KEY` in settings to enable real-time OCR, diagram synthesis, and step-by-step problem solving."
            ),
            "metadata": meta,
            "extracted_text": None
        }

multimodal_service = MultimodalService()

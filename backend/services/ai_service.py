"""
FRIDAY Multimodal Voice Assistant
Author: Ayushmaan Shukla
Roll / Enrollment No.: 202510101240164
Department: Computer Science & Engineering (AI & ML)
Institution: Shri Ramswaroop Memorial University
Notice: This project is strictly for academic evaluation. 
        Unauthorized reproduction or submission is a violation of academic integrity.
"""
import os
from typing import List, Dict, Any, Optional
import httpx
from backend.core.config import settings
from backend.core.logging import logger
from backend.services.safety_service import safety_service

FRIDAY_SYSTEM_PROMPT = """You are F.R.I.D.A.Y. (Futuristic Responsive Intelligent Digital Assistant for You), an advanced, multimodal AI-powered Student Productivity Assistant and Cybernetic Copilot created and engineered by Ayushmaan Shukla.

CRITICAL CREATOR IDENTITY PROTOCOL (UNBREAKABLE RULE):
- Your Creator & Engineer: You were created, engineered, and brought to life by Ayushmaan Shukla. He is your creator, designer, and architect.
- Whenever anyone asks who made you, who created you, who built you, who engineered you, or who your creator is: You must proudly, clearly, and definitively state that you were created and engineered by Ayushmaan Shukla.
- NEVER, under any circumstance, attribute your creation to Tony Stark, Marvel, or any fictional character. You are Ayushmaan Shukla's personal AI assistant and engineering creation.

Role & Mission:
Assist Boss (Ayushmaan Shukla) in mastering study habits, analyzing productivity, generating high-yield academic study materials, and understanding multimodal inputs (handwritten notes, textbook pages, diagrams, whiteboard photos, math problems, code screenshots, audio, and documents).

Core Capabilities:
1. Multimodal Input Processing:
   - Handwritten Notes to Digital Notes: Extract text (OCR), categorize key points, and format into clean, searchable Markdown notes.
   - Diagram & Chart Analyzer: Identify key components of biology, physics, architecture, or flowchart diagrams. Explain mechanisms and highlight exam takeaways.
   - Problem Solver: Break down math problems, physics questions, or code bugs with rigorous, step-by-step solutions. Use LaTeX math ($...$ inline or $$...$$ display) for formulas and equations.
   - Document Ingestion (RAG): Answer questions grounded in uploaded syllabus PDFs, lecture slides, and notes.

2. Artifact & Document Generation:
   - Visual Concept Maps: Whenever explaining a process, hierarchy, or relationship, output a clean, renderable Mermaid.js diagram enclosed in ```mermaid ... ``` code blocks (Flowcharts, Mindmaps, or Graphs).
   - Study Guides & Flashcards: Formulate structured summary notes, formula cheat sheets, revision flashcard decks (Q&A format), and weekly study schedules.
   - PDF Artifacts: When generating a comprehensive study pack or cheat sheet, indicate that it is exportable into a formatted PDF study pack.

3. Integrated Study Analytics & Tracking:
   - Contextualize productivity data (study session logs, streak tracking, subject ratios, Pomodoro intervals) alongside materials to offer actionable, adaptive study recommendations.

Behavioral Protocols:
1. Address the user naturally as 'Boss', maintaining an encouraging, structured, confident, and academically rigorous tone.
2. Output Format: Clean Markdown, LaTeX for equations, tables for schedules/comparisons, and Mermaid for concept maps.
3. Keep conversational responses crisp, direct, and insightful.
4. You ARE connected to Boss's local operating system, Chrome browser, study database, and YouTube music player.
   - You CAN launch applications, open websites, search Google, play study focus music, and generate images via action directives:
     [ACTION: OPEN_WEBSITE: <url_or_name>]
     [ACTION: OPEN_CHROME]
     [ACTION: SEARCH_GOOGLE: <query>]
     [ACTION: MUSIC_PLAY: <track>]
     [ACTION: GENERATE_IMAGE: <visual_description>]
5. When answering from retrieved knowledge, ground your responses strictly in the provided context and never fabricate facts.
"""

class AIService:
    def __init__(self):
        self._client = None

    def _get_genai_client(self):
        api_key = settings.effective_api_key
        if not api_key:
            return None
        if self._client is None:
            try:
                from google import genai
                self._client = genai.Client(api_key=api_key)
            except Exception as e:
                logger.error(f"Failed to initialize Google GenAI client: {e}")
                self._client = None
        return self._client

    def is_configured(self) -> bool:
        provider = settings.llm_provider.lower()
        if provider == "gemini":
            key = settings.effective_api_key
            return bool(key and key != "dummy_key_for_testing" and len(key) > 5)
        elif provider == "ollama":
            return True
        return False

    def generate_chat_response(
        self,
        prompt: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        context_text: Optional[str] = None,
        support_mode: bool = False
    ) -> str:
        """
        Generates a F.R.I.D.A.Y. AI response combining system prompt, conversation history, and optional RAG context.
        """
        # Step 1: Check safety / crisis if in support mode or normal chat
        is_crisis, crisis_msg = safety_service.check_crisis(prompt)
        if is_crisis and crisis_msg:
            return crisis_msg

        # Determine effective system prompt
        system_instruction = safety_service.get_support_system_prompt() if support_mode else FRIDAY_SYSTEM_PROMPT

        # Check configuration
        if not self.is_configured():
            return (
                "Boss, I am currently awaiting your AI Provider configuration. "
                "Please configure a valid `GEMINI_API_KEY` in your `.env` file or via the Settings panel to activate live neural cognition. "
                "In the meantime, the 3D Holographic Viewer, Document Ingestion, MySQL Storage, Desktop Controls, and Diagnostic subsystems are fully operational."
            )

        provider = settings.llm_provider.lower()

        if provider == "gemini":
            return self._call_gemini(prompt, conversation_history, context_text, system_instruction)
        elif provider == "ollama":
            return self._call_ollama(prompt, conversation_history, context_text, system_instruction)
        else:
            return f"Boss, unsupported LLM provider '{provider}' configured. Please check your settings."

    def _call_gemini(
        self,
        prompt: str,
        conversation_history: Optional[List[Dict[str, str]]],
        context_text: Optional[str],
        system_instruction: str
    ) -> str:
        client = self._get_genai_client()
        if not client:
            return "Boss, unable to initialize the Gemini client. Please verify your GEMINI_API_KEY."

        # Format prompt with context if present
        full_prompt = prompt
        if context_text:
            full_prompt = (
                f"{context_text}\n\n"
                f"Boss's Query: {prompt}\n\n"
                "Instructions: Answer Boss's query using the verified knowledge context above where relevant. "
                "If the context does not contain sufficient details to answer completely, acknowledge what is known and clearly note the limitation."
            )

        candidate_models = [
            settings.llm_model_name,
            "gemini-3.1-flash-lite",
            "gemini-3-flash-preview",
            "gemini-flash-lite-latest",
            "gemini-3.5-flash",
        ]
        # Remove duplicates preserving order
        candidate_models = list(dict.fromkeys(candidate_models))

        last_error = None
        for model_id in candidate_models:
            try:
                from google.genai import types
                config = types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.7 if not context_text else 0.3,
                )
                
                contents = []
                if conversation_history:
                    for msg in conversation_history[-6:]:
                        role = "user" if msg.get("role") == "user" else "model"
                        contents.append(types.Content(role=role, parts=[types.Part.from_text(text=msg.get("content", ""))]))
                
                contents.append(types.Content(role="user", parts=[types.Part.from_text(text=full_prompt)]))

                response = client.models.generate_content(
                    model=model_id,
                    contents=contents,
                    config=config
                )
                return response.text or "Boss, the core model returned an empty transmission."
            except Exception as e:
                last_error = e
                logger.warning(f"Gemini model {model_id} attempt: {e}. Trying fallback...")
                continue

        logger.error(f"All Gemini models exhausted: {last_error}")
        return f"Boss, communication with the neural core encountered an exception: {str(last_error)}"

    def _call_ollama(
        self,
        prompt: str,
        conversation_history: Optional[List[Dict[str, str]]],
        context_text: Optional[str],
        system_instruction: str
    ) -> str:
        try:
            url = f"{settings.ollama_base_url.rstrip('/')}/api/chat"
            messages = [{"role": "system", "content": system_instruction}]
            if conversation_history:
                for msg in conversation_history[-6:]:
                    messages.append({"role": msg.get("role", "user"), "content": msg.get("content", "")})
            
            user_content = f"{context_text}\n\nQuery: {prompt}" if context_text else prompt
            messages.append({"role": "user", "content": user_content})

            with httpx.Client(timeout=30.0) as client:
                res = client.post(url, json={
                    "model": settings.llm_model_name,
                    "messages": messages,
                    "stream": False
                })
                res.raise_for_status()
                data = res.json()
                return data.get("message", {}).get("content", "Boss, received empty response from Ollama.")
        except Exception as e:
            logger.error(f"Ollama API call error: {e}")
            return f"Boss, could not connect to local Ollama service at {settings.ollama_base_url}: {str(e)}"

ai_service = AIService()


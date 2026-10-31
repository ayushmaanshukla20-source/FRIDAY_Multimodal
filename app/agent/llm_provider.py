from abc import ABC, abstractmethod
from google import genai
from config.settings import settings

class LLMProvider(ABC):
    @abstractmethod
    def generate_text(self, prompt: str) -> str:
        """Generate text from the LLM based on a given prompt."""
        pass

class GeminiProvider(LLMProvider):
    def __init__(self):
        api_key = settings.gemini_api_key or "DUMMY_KEY"
        self.client = genai.Client(api_key=api_key)
        self.model_name = settings.llm_model_name

    def generate_text(self, prompt: str) -> str:
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt
        )
        return response.text or ""

class MockProvider(LLMProvider):
    def generate_text(self, prompt: str) -> str:
        return f"[JARVIS Mock LLM] Received prompt: {prompt}. (Configure GEMINI_API_KEY in .env for live Gemini Flash responses)"

def get_llm_provider() -> LLMProvider:
    provider = settings.llm_provider.lower()
    if provider == "gemini":
        if not settings.gemini_api_key or settings.gemini_api_key == "dummy_key_for_testing":
            # If no real API key is configured, fallback to Mock or prompt user
            return MockProvider()
        return GeminiProvider()
    elif provider in ("mock", "test"):
        return MockProvider()
    
    raise ValueError(f"Unsupported LLM provider: {provider}")

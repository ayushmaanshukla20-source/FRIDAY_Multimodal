import math
import hashlib
from typing import List
from backend.core.config import settings
from backend.core.logging import logger

class EmbeddingService:
    def __init__(self):
        self.dimension = 384
        self._gemini_client = None

    def _get_gemini_client(self):
        if self._gemini_client is None and settings.effective_api_key:
            try:
                from google import genai
                self._gemini_client = genai.Client(api_key=settings.effective_api_key)
            except Exception as e:
                logger.warning(f"Could not initialize GenAI client for embeddings: {e}")
        return self._gemini_client

    def embed_text(self, text: str) -> List[float]:
        """Generates embedding for a single text block."""
        embeddings = self.embed_batch([text])
        return embeddings[0] if embeddings else [0.0] * self.dimension

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generates embeddings for a batch of text blocks."""
        if not texts:
            return []

        client = self._get_gemini_client()
        if client and settings.effective_api_key:
            try:
                # Use Google GenAI embedding API
                results = []
                for t in texts:
                    res = client.models.embed_content(
                        model=settings.embedding_model_name,
                        contents=t
                    )
                    # Extract embedding vector
                    if hasattr(res, "embedding") and hasattr(res.embedding, "values"):
                        results.append(list(res.embedding.values))
                    elif hasattr(res, "embeddings") and len(res.embeddings) > 0:
                        results.append(list(res.embeddings[0].values))
                    else:
                        results.append(self._fallback_embed(t))
                return results
            except Exception as e:
                logger.warning(f"Live embedding API call failed ({e}). Falling back to local deterministic vectorizer.")

        # Local deterministic semantic feature hashing fallback
        return [self._fallback_embed(t) for t in texts]

    def _fallback_embed(self, text: str) -> List[float]:
        """
        Deterministic, L2-normalized 384-dimensional feature hash embedding.
        Captures word and subword frequencies for local semantic similarity and testing.
        """
        vec = [0.0] * self.dimension
        words = text.lower().split()
        if not words:
            return vec

        for word in words:
            # Hash word and character n-grams
            h = int(hashlib.md5(word.encode("utf-8")).hexdigest(), 16)
            idx = h % self.dimension
            sign = 1.0 if ((h >> 8) & 1) else -1.0
            vec[idx] += sign

            # Bigrams
            for i in range(len(word) - 2):
                bg = word[i:i+3]
                h_bg = int(hashlib.sha256(bg.encode("utf-8")).hexdigest(), 16)
                idx_bg = h_bg % self.dimension
                vec[idx_bg] += 0.5

        # L2 normalize
        norm = math.sqrt(sum(v * v for v in vec))
        if norm > 1e-9:
            vec = [v / norm for v in vec]
        return vec

embedding_service = EmbeddingService()

"""
Embedding service using Ollama for RAG implementation.
Generates vector embeddings for semantic search.
"""

import logging
import requests
from typing import List, Dict, Any
from django.conf import settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """
    Service for generating embeddings using Ollama.
    Uses nomic-embed-text model for text embeddings.
    """

    def __init__(self):
        """Initialize embedding service."""
        self.ollama_host = settings.OLLAMA_SETTINGS['HOST']
        self.embedding_model = 'nomic-embed-text'
        self.embedding_dimension = 768  # nomic-embed-text dimension

    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding vector for a single text.

        Args:
            text: Input text to embed

        Returns:
            List of floats representing the embedding vector
        """
        if not text or not text.strip():
            logger.warning("Empty text provided for embedding")
            return [0.0] * self.embedding_dimension

        try:
            response = requests.post(
                f"{self.ollama_host}/api/embeddings",
                json={
                    "model": self.embedding_model,
                    "prompt": text
                },
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                embedding = result.get('embedding', [])

                if len(embedding) != self.embedding_dimension:
                    logger.warning(
                        f"Unexpected embedding dimension: {len(embedding)}, "
                        f"expected {self.embedding_dimension}"
                    )

                return embedding
            else:
                logger.error(
                    f"Ollama embedding failed with status {response.status_code}: "
                    f"{response.text}"
                )
                return [0.0] * self.embedding_dimension

        except Exception as e:
            logger.error(f"Failed to generate embedding: {str(e)}")
            return [0.0] * self.embedding_dimension

    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of input texts

        Returns:
            List of embedding vectors
        """
        embeddings = []
        for text in texts:
            embedding = self.generate_embedding(text)
            embeddings.append(embedding)
        return embeddings

    def ensure_model_available(self) -> bool:
        """
        Check if the embedding model is available in Ollama.
        Pull it if not available.

        Returns:
            True if model is available, False otherwise
        """
        try:
            # Check if model exists
            response = requests.get(
                f"{self.ollama_host}/api/tags",
                timeout=5
            )

            if response.status_code == 200:
                models = response.json().get('models', [])
                model_names = [m.get('name', '') for m in models]

                if self.embedding_model in model_names:
                    logger.info(f"Embedding model '{self.embedding_model}' is available")
                    return True
                else:
                    logger.warning(
                        f"Embedding model '{self.embedding_model}' not found. "
                        f"Please pull it with: ollama pull {self.embedding_model}"
                    )
                    return False
            else:
                logger.error(f"Failed to check Ollama models: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"Failed to check model availability: {str(e)}")
            return False


# Singleton instance
embedding_service = EmbeddingService()

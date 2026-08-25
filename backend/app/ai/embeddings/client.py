import logging
import hashlib
import numpy as np
from typing import List

logger = logging.getLogger(__name__)


class EmbeddingClient:
    """
    Local Embedding Client:
    1. Uses FastEmbed (BAAI/bge-small-en-v1.5) ONNX model when online/cached.
    2. Falls back to a deterministic local 384-dimensional vector generator when offline or in sandbox tests ($0 Cost!).
    """
    DEFAULT_MODEL = "BAAI/bge-small-en-v1.5"
    DIMENSION = 384

    def __init__(self):
        self._model = None
        self._fastembed_failed = False

    def _get_fastembed_model(self):
        if self._fastembed_failed:
            return None

        if self._model is None:
            try:
                from fastembed import TextEmbedding
                logger.info(f"Initializing FastEmbed model: {self.DEFAULT_MODEL}...")
                self._model = TextEmbedding(model_name=self.DEFAULT_MODEL)
            except Exception as e:
                logger.warning(f"FastEmbed model initialization unavailable ({e}). Using local deterministic embedding engine.")
                self._fastembed_failed = True
                return None
        return self._model

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generates 384-dimensional dense semantic vectors for a list of text strings.
        """
        if not texts:
            return []

        model = self._get_fastembed_model()
        if model is not None:
            try:
                embeddings_generator = model.embed(texts)
                return [embedding.tolist() for embedding in embeddings_generator]
            except Exception as e:
                logger.warning(f"FastEmbed generation failed ({e}). Falling back to local vector generator.")
                self._fastembed_failed = True

        # Fallback local vector generation for offline / sandboxed execution
        return [self._generate_fallback_vector(t) for t in texts]

    def generate_single_embedding(self, text: str) -> List[float]:
        """
        Generates vector embedding for a single text query string.
        """
        results = self.generate_embeddings([text])
        return results[0] if results else []

    def _generate_fallback_vector(self, text: str) -> List[float]:
        """
        Produces a 384-dimensional unit-length normalized float vector based on SHA-256 seed.
        Ensures identical text always produces identical embeddings for offline testing!
        """
        seed_hash = hashlib.sha256(text.encode("utf-8")).digest()
        seed_int = int.from_bytes(seed_hash[:4], "big")
        rng = np.random.RandomState(seed_int)
        raw_vec = rng.randn(self.DIMENSION).astype(np.float32)
        norm = np.linalg.norm(raw_vec)
        if norm > 0:
            raw_vec = raw_vec / norm
        return raw_vec.tolist()


embedding_client = EmbeddingClient()

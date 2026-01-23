"""
Embedding module for generating text embeddings using HuggingFace models.
Handles model initialization and embedding generation.
"""

from sentence_transformers import SentenceTransformer
from app.config import settings
import logging
from typing import List, Union

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmbeddingModel:
    """Wrapper for sentence-transformers embedding model."""
    
    def __init__(self):
        """Initialize the embedding model."""
        self.model = None
        self.model_name = settings.EMBEDDING_MODEL_NAME
    
    def load_model(self):
        """
        Load the sentence-transformers model.
        This downloads the model if not cached locally.
        
        Returns:
            bool: True if model loaded successfully
        """
        try:
            logger.info(f"Loading embedding model: {self.model_name}")
            
            # Load the model - it will download if not cached
            self.model = SentenceTransformer(self.model_name)
            
            logger.info(f"Model loaded successfully. Embedding dimension: {self.model.get_sentence_embedding_dimension()}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return False
    
    def get_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Input text to embed
            
        Returns:
            List[float]: Embedding vector
        """
        if self.model is None:
            self.load_model()
        
        if not text or not isinstance(text, str):
            logger.warning("Invalid text input, returning zero vector")
            return [0.0] * settings.VECTOR_DIMENSION
        
        try:
            # Generate embedding
            embedding = self.model.encode(text, convert_to_tensor=False)
            return embedding.tolist()
            
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return [0.0] * settings.VECTOR_DIMENSION
    
    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts (batch processing).
        
        Args:
            texts: List of input texts
            
        Returns:
            List[List[float]]: List of embedding vectors
        """
        if self.model is None:
            self.load_model()
        
        if not texts:
            return []
        
        try:
            # Batch encode for better performance
            embeddings = self.model.encode(texts, convert_to_tensor=False, show_progress_bar=True)
            return [emb.tolist() for emb in embeddings]
            
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {e}")
            return [[0.0] * settings.VECTOR_DIMENSION] * len(texts)
    
    def get_dimension(self) -> int:
        """
        Get the dimension of the embedding vectors.
        
        Returns:
            int: Embedding dimension
        """
        if self.model is None:
            self.load_model()
        
        return self.model.get_sentence_embedding_dimension()


# Create a global embedding model instance
embedding_model = EmbeddingModel()

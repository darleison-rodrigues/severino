from sentence_transformers import SentenceTransformer
from typing import List
import logging

logger = logging.getLogger(__name__)

# Global instance of the SentenceTransformer model
_embedding_model = None

def load_embedding_model(model_name: str = "all-MiniLM-L6-v2"):
    """
    Loads a pre-trained SentenceTransformer model.
    Uses a singleton pattern to ensure the model is loaded only once.
    """
    global _embedding_model
    if _embedding_model is None:
        try:
            logger.info(f"Loading SentenceTransformer model: {model_name}")
            _embedding_model = SentenceTransformer(model_name)
            logger.info("SentenceTransformer model loaded successfully.")
        except Exception as e:
            logger.error(f"Error loading SentenceTransformer model {model_name}: {e}", exc_info=True)
            _embedding_model = None
            raise
    return _embedding_model

def generate_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Generates embeddings for a list of texts using the loaded model.
    """
    if _embedding_model is None:
        raise RuntimeError("Embedding model not loaded. Call load_embedding_model() first.")
    
    logger.info(f"Generating embeddings for {len(texts)} texts.")
    embeddings = _embedding_model.encode(texts).tolist()
    logger.info("Embeddings generated successfully.")
    return embeddings

# Example Usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    try:
        model = load_embedding_model()
        texts_to_embed = [
            "This is a sentence about machine learning.",
            "ML models are very useful for data analysis.",
            "The quick brown fox jumps over the lazy dog."
        ]
        embeddings = generate_embeddings(texts_to_embed)
        print(f"Generated {len(embeddings)} embeddings, each with dimension {len(embeddings[0])}.")
        # print(embeddings)

        # Test with a different model (will load only once)
        model_large = load_embedding_model("all-MiniLM-L12-v2")
        print(f"Loaded model: {model_large.default_model}")

    except Exception as e:
        print(f"An error occurred: {e}")

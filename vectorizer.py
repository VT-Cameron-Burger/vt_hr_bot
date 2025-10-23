# vectorizer.py
# Core vectorization functionality and similarity search

import os
import logging
import pickle
from typing import List, Dict, Any

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    print("sentence-transformers not found. Install with: pip install sentence-transformers")
    SentenceTransformer = None

try:
    import numpy as np
except ImportError:
    print("numpy not found. Install with: pip install numpy")
    np = None

from pdf_processor import PDFProcessor

logger = logging.getLogger(__name__)

class DocumentVectorizer:
    """Handles document vectorization and similarity search"""
    
    def __init__(self, model_name: str = 'all-mpnet-base-v2'):
        """
        Initialize the document vectorizer
        
        Args:
            model_name: Name of the sentence transformer model to use
                      Default: 'all-mpnet-base-v2' - Better for professional/HR documents
                      Alternative options:
                      - 'all-MiniLM-L6-v2': Faster but less accurate
                      - 'multi-qa-mpnet-base-dot-v1': Optimized for Q&A
                      - 'all-distilroberta-v1': Good for policy documents
        """
        if SentenceTransformer is None:
            raise ImportError("sentence-transformers is required. Install with: pip install sentence-transformers")
        
        self.model = SentenceTransformer(model_name)
        self.model_name = model_name
        self.documents = []
        self.embeddings = None
        self.metadata = []
    
    def vectorize_documents(self, documents: List[str], metadata: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate embeddings for a list of documents
        
        Args:
            documents: List of text documents to vectorize
            metadata: List of metadata dictionaries for each document
            
        Returns:
            Dictionary containing documents, embeddings, and metadata
        """
        if not documents:
            logger.warning("No documents provided for vectorization")
            return {"documents": [], "embeddings": [], "metadata": []}
        
        logger.info(f"Generating embeddings for {len(documents)} documents...")
        embeddings = self.model.encode(documents, show_progress_bar=True)
        
        # Store results
        self.documents = documents
        self.embeddings = embeddings
        self.metadata = metadata
        
        return {
            "documents": documents,
            "embeddings": embeddings,
            "metadata": metadata
        }
    
    def find_similar_documents(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Find documents similar to the query
        
        Args:
            query: Search query
            top_k: Number of top similar documents to return
            
        Returns:
            List of similar documents with metadata and similarity scores
        """
        if self.embeddings is None:
            raise ValueError("No embeddings found. Run vectorize_documents() or load_vectors() first.")
        
        if np is None:
            raise ImportError("numpy is required for similarity calculations")
        
        # Encode query
        query_embedding = self.model.encode([query])
        
        # Calculate similarities
        similarities = np.dot(self.embeddings, query_embedding.T).flatten()
        
        # Get top k indices
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            results.append({
                "document": self.documents[idx],
                "metadata": self.metadata[idx],
                "similarity_score": float(similarities[idx])
            })
        
        return results
    
    def save_vectors(self, output_path: str = "pdf_vectors.pkl"):
        """
        Save the vectorized data to a pickle file
        
        Args:
            output_path: Path to save the vectorized data
        """
        if self.embeddings is None:
            raise ValueError("No embeddings found. Run vectorize_documents() first.")
        
        data = {
            "documents": self.documents,
            "embeddings": self.embeddings,
            "metadata": self.metadata,
            "model_name": self.model_name,
            "embedding_dimension": self.model.get_sentence_embedding_dimension()
        }
        
        with open(output_path, 'wb') as f:
            pickle.dump(data, f)
        
        logger.info(f"Vectors saved to {output_path}")
    
    def load_vectors(self, input_path: str = "pdf_vectors.pkl"):
        """
        Load vectorized data from a pickle file
        
        Args:
            input_path: Path to load the vectorized data from
        """
        with open(input_path, 'rb') as f:
            data = pickle.load(f)
        
        self.documents = data["documents"]
        self.embeddings = data["embeddings"]
        self.metadata = data["metadata"]
        
        logger.info(f"Vectors loaded from {input_path}")
        
        # Log model info if available
        if "model_name" in data:
            logger.info(f"Original model: {data['model_name']}")
        if "embedding_dimension" in data:
            logger.info(f"Embedding dimension: {data['embedding_dimension']}")
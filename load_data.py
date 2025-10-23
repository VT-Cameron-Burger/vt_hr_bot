# load_data.py
# This file contains functions for loading and processing data

import os
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import pickle

try:
    import PyPDF2
except ImportError:
    print("PyPDF2 not found. Install with: pip install PyPDF2")
    PyPDF2 = None

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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFVectorizer:
    """Class to handle PDF vectorization for AI agents"""
    
    def __init__(self, model_name: str = 'all-mpnet-base-v2'):
        """
        Initialize the PDF vectorizer
        
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
        self.documents = []
        self.embeddings = None
        self.metadata = []
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract text from a PDF file
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Extracted text as string
        """
        if PyPDF2 is None:
            raise ImportError("PyPDF2 is required. Install with: pip install PyPDF2")
        
        text = ""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            logger.error(f"Error extracting text from {pdf_path}: {e}")
            return ""
        
        return text.strip()
    
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """
        Split text into chunks for better vectorization
        
        Args:
            text: Text to chunk
            chunk_size: Maximum size of each chunk
            overlap: Number of characters to overlap between chunks
            
        Returns:
            List of text chunks
        """
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            
            # Try to break at sentence boundary
            if end < len(text):
                last_period = chunk.rfind('.')
                last_newline = chunk.rfind('\n')
                break_point = max(last_period, last_newline)
                
                if break_point > start + chunk_size // 2:
                    chunk = text[start:break_point + 1]
                    end = break_point + 1
            
            chunks.append(chunk.strip())
            start = end - overlap if end < len(text) else end
        
        return [chunk for chunk in chunks if chunk.strip()]
    
    def vectorize_pdfs(self, pdf_directory: str = "downloaded_pdfs", 
                      chunk_size: int = 1000, overlap: int = 200) -> Dict[str, Any]:
        """
        Vectorize all PDFs in the specified directory
        
        Args:
            pdf_directory: Directory containing PDF files
            chunk_size: Size of text chunks for vectorization
            overlap: Overlap between chunks
            
        Returns:
            Dictionary containing documents, embeddings, and metadata
        """
        pdf_dir = Path(pdf_directory)
        if not pdf_dir.exists():
            raise FileNotFoundError(f"Directory {pdf_directory} not found")
        
        pdf_files = list(pdf_dir.glob("*.pdf"))
        if not pdf_files:
            logger.warning(f"No PDF files found in {pdf_directory}")
            return {"documents": [], "embeddings": [], "metadata": []}
        
        logger.info(f"Found {len(pdf_files)} PDF files to process")
        
        all_documents = []
        all_metadata = []
        
        for pdf_file in pdf_files:
            logger.info(f"Processing {pdf_file.name}")
            
            # Extract text
            text = self.extract_text_from_pdf(str(pdf_file))
            if not text:
                logger.warning(f"No text extracted from {pdf_file.name}")
                continue
            
            # Chunk text
            chunks = self.chunk_text(text, chunk_size, overlap)
            
            # Add to documents and metadata
            for i, chunk in enumerate(chunks):
                all_documents.append(chunk)
                all_metadata.append({
                    "source_file": pdf_file.name,
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "file_path": str(pdf_file)
                })
        
        logger.info(f"Total text chunks created: {len(all_documents)}")
        
        # Generate embeddings
        if all_documents:
            logger.info("Generating embeddings...")
            embeddings = self.model.encode(all_documents, show_progress_bar=True)
            
            # Store results
            self.documents = all_documents
            self.embeddings = embeddings
            self.metadata = all_metadata
            
            return {
                "documents": all_documents,
                "embeddings": embeddings,
                "metadata": all_metadata
            }
        else:
            return {"documents": [], "embeddings": [], "metadata": []}
    
    def save_vectors(self, output_path: str = "pdf_vectors.pkl"):
        """
        Save the vectorized data to a pickle file
        
        Args:
            output_path: Path to save the vectorized data
        """
        if self.embeddings is None:
            raise ValueError("No embeddings found. Run vectorize_pdfs() first.")
        
        data = {
            "documents": self.documents,
            "embeddings": self.embeddings,
            "metadata": self.metadata,
            "model_name": self.model.get_sentence_embedding_dimension()
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
            raise ValueError("No embeddings found. Run vectorize_pdfs() or load_vectors() first.")
        
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

    def compare_models(self, test_queries: List[str], model_names: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Compare different embedding models on test queries
        
        Args:
            test_queries: List of test queries to evaluate
            model_names: List of model names to compare
            
        Returns:
            Comparison results for each model
        """
        if model_names is None:
            model_names = [
                'all-mpnet-base-v2',
                'all-MiniLM-L6-v2', 
                'multi-qa-mpnet-base-dot-v1',
                'all-distilroberta-v1'
            ]
        
        if SentenceTransformer is None:
            raise ImportError("sentence-transformers is required for model comparison")
        
        results = {}
        original_model = self.model
        
        for model_name in model_names:
            print(f"\nTesting model: {model_name}")
            try:
                # Load model
                self.model = SentenceTransformer(model_name)
                
                model_results = []
                for query in test_queries:
                    similar_docs = self.find_similar_documents(query, top_k=3)
                    model_results.append({
                        "query": query,
                        "top_similarity": similar_docs[0]["similarity_score"] if similar_docs else 0,
                        "results": similar_docs
                    })
                
                results[model_name] = {
                    "avg_top_similarity": sum(r["top_similarity"] for r in model_results) / len(model_results),
                    "results": model_results
                }
                
            except Exception as e:
                print(f"Error testing {model_name}: {e}")
                results[model_name] = {"error": str(e)}
        
        # Restore original model
        self.model = original_model
        return results

def test_model_performance():
    """
    Test the performance of different models on HR-specific queries
    """
    try:
        # Load existing vectors or create new ones
        vectorizer = load_data()
        if not vectorizer:
            print("Failed to load vectorizer")
            return None, None
        
        # HR-specific test queries
        test_queries = [
            "employee benefits and compensation",
            "vacation leave policy",
            "performance evaluation process",
            "workplace harassment policy",
            "retirement plans and 401k",
            "employee training and development"
        ]
        
        print("Testing current model performance...")
        current_results = []
        for query in test_queries:
            results = vectorizer.find_similar_documents(query, top_k=3)
            current_results.append({
                "query": query,
                "top_similarity": results[0]["similarity_score"] if results else 0,
                "source": results[0]["metadata"]["source_file"] if results else "N/A"
            })
        
        print("\nCurrent Model Performance:")
        for result in current_results:
            print(f"Query: {result['query']}")
            print(f"  Best match: {result['source']} (similarity: {result['top_similarity']:.4f})")
        
        avg_similarity = sum(r["top_similarity"] for r in current_results) / len(current_results)
        print(f"\nAverage similarity score: {avg_similarity:.4f}")
        
        return vectorizer, current_results
        
    except Exception as e:
        logger.error(f"Error in test_model_performance: {e}")
        return None, None

def load_data():
    """
    Main function to load and vectorize PDF data
    """
    try:
        vectorizer = PDFVectorizer()
        
        # Check if vectors already exist
        if os.path.exists("pdf_vectors.pkl"):
            print("Loading existing vectors...")
            vectorizer.load_vectors()
        else:
            print("Vectorizing PDFs...")
            result = vectorizer.vectorize_pdfs()
            
            if result["documents"]:
                vectorizer.save_vectors()
                print(f"Successfully vectorized {len(result['documents'])} text chunks")
            else:
                print("No documents were processed")
        
        return vectorizer
        
    except Exception as e:
        logger.error(f"Error in load_data: {e}")
        return None

if __name__ == "__main__":
    print("=== HR Document Vectorization System ===")
    print("Now using all-mpnet-base-v2 for better HR document understanding")
    print()
    
    # Test the new model performance
    vectorizer, test_results = test_model_performance()
    
    if vectorizer:
        print("\n=== Interactive Testing ===")
        
        # Example usage with HR-specific queries
        hr_queries = [
            "employee benefits",
            "vacation policy", 
            "performance review",
            "workplace safety"
        ]
        
        for query in hr_queries:
            print(f"\nSearching for: '{query}'")
            results = vectorizer.find_similar_documents(query, top_k=2)
            
            for i, result in enumerate(results):
                print(f"  {i+1}. Source: {result['metadata']['source_file']}")
                print(f"     Similarity: {result['similarity_score']:.4f}")
                print(f"     Preview: {result['document'][:150]}...")
                print()
    
    print("\n=== Model Information ===")
    print("Current model: all-mpnet-base-v2")
    print("- 768-dimensional embeddings")
    print("- Optimized for professional/HR documents")
    print("- Better context understanding than MiniLM")
    print("- Suitable for policy and regulatory text")
    print("\nTo compare models, run:")
    print("vectorizer.compare_models(['employee benefits', 'vacation policy'])")
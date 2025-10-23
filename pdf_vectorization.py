# pdf_vectorization.py  
# Main interface for PDF vectorization system

import os
import logging
from pathlib import Path
from typing import Dict, Any

from pdf_processor import PDFProcessor
from vectorizer import DocumentVectorizer
from model_comparison import ModelComparison

logger = logging.getLogger(__name__)

class PDFVectorization:
    """Main interface for PDF vectorization system"""
    
    def __init__(self, model_name: str = 'all-mpnet-base-v2'):
        """
        Initialize the PDF vectorization system
        
        Args:
            model_name: Embedding model to use
        """
        self.pdf_processor = PDFProcessor()
        self.vectorizer = DocumentVectorizer(model_name)
        self.model_comparison = ModelComparison(self.vectorizer)
    
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
        # Get PDF files
        pdf_files = self.pdf_processor.get_pdf_files(pdf_directory)
        if not pdf_files:
            logger.warning(f"No PDF files found in {pdf_directory}")
            return {"documents": [], "embeddings": [], "metadata": []}
        
        logger.info(f"Found {len(pdf_files)} PDF files to process")
        
        all_documents = []
        all_metadata = []
        
        for pdf_file in pdf_files:
            logger.info(f"Processing {pdf_file.name}")
            
            # Extract text
            text = self.pdf_processor.extract_text_from_pdf(str(pdf_file))
            if not text:
                logger.warning(f"No text extracted from {pdf_file.name}")
                continue
            
            # Chunk text
            chunks = self.pdf_processor.chunk_text(text, chunk_size, overlap)
            
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
        return self.vectorizer.vectorize_documents(all_documents, all_metadata)
    
    def load_or_create_vectors(self, vector_file: str = "pdf_vectors.pkl") -> bool:
        """
        Load existing vectors or create new ones
        
        Args:
            vector_file: Path to vector file
            
        Returns:
            True if vectors were loaded/created successfully
        """
        try:
            if os.path.exists(vector_file):
                print("Loading existing vectors...")
                self.vectorizer.load_vectors(vector_file)
                return True
            else:
                print("Vectorizing PDFs...")
                result = self.vectorize_pdfs()
                
                if result["documents"]:
                    self.vectorizer.save_vectors(vector_file)
                    print(f"Successfully vectorized {len(result['documents'])} text chunks")
                    return True
                else:
                    print("No documents were processed")
                    return False
        except Exception as e:
            logger.error(f"Error loading/creating vectors: {e}")
            return False
    
    def search(self, query: str, top_k: int = 5):
        """
        Search for similar documents
        
        Args:
            query: Search query
            top_k: Number of results to return
            
        Returns:
            List of similar documents
        """
        return self.vectorizer.find_similar_documents(query, top_k)
    
    def compare_models(self, test_queries=None):
        """
        Compare different embedding models
        
        Args:
            test_queries: List of test queries (uses HR defaults if None)
        """
        if test_queries is None:
            test_queries = ModelComparison.get_hr_test_queries()
        
        results = self.model_comparison.compare_models(test_queries)
        ModelComparison.print_comparison_results(results)
        return results
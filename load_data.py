# load_data.py
# Data loading utilities for the PDF vectorization system

import logging
from pdf_vectorization import PDFVectorization

logger = logging.getLogger(__name__)

def load_data(model_name: str = 'all-mpnet-base-v2'):
    """
    Load and vectorize PDF data
    
    Args:
        model_name: Name of the embedding model to use
        
    Returns:
        PDFVectorization system instance or None if failed
    """
    try:
        system = PDFVectorization(model_name)
        success = system.load_or_create_vectors()
        
        if success:
            return system
        else:
            return None
        
    except Exception as e:
        logger.error(f"Error in load_data: {e}")
        return None

def load_existing_vectors(vector_file: str = "pdf_vectors.pkl", model_name: str = 'all-mpnet-base-v2'):
    """
    Load existing vectors without creating new ones
    
    Args:
        vector_file: Path to the vector file
        model_name: Name of the embedding model to use
        
    Returns:
        PDFVectorization system instance or None if failed
    """
    try:
        system = PDFVectorization(model_name)
        system.vectorizer.load_vectors(vector_file)
        return system
        
    except Exception as e:
        logger.error(f"Error loading existing vectors: {e}")
        return None

def create_new_vectors(pdf_directory: str = "downloaded_pdfs", 
                      model_name: str = 'all-mpnet-base-v2',
                      vector_file: str = "pdf_vectors.pkl"):
    """
    Create new vectors from PDFs (ignoring existing vectors)
    
    Args:
        pdf_directory: Directory containing PDF files
        model_name: Name of the embedding model to use  
        vector_file: Path to save the vectors
        
    Returns:
        PDFVectorization system instance or None if failed
    """
    try:
        system = PDFVectorization(model_name)
        result = system.vectorize_pdfs(pdf_directory)
        
        if result["documents"]:
            system.vectorizer.save_vectors(vector_file)
            logger.info(f"Successfully created vectors for {len(result['documents'])} text chunks")
            return system
        else:
            logger.warning("No documents were processed")
            return None
        
    except Exception as e:
        logger.error(f"Error creating new vectors: {e}")
        return None
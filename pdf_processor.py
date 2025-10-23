# pdf_processor.py
# Handles PDF text extraction and text chunking

import logging
from pathlib import Path
from typing import List

try:
    import PyPDF2
except ImportError:
    print("PyPDF2 not found. Install with: pip install PyPDF2")
    PyPDF2 = None

logger = logging.getLogger(__name__)

class PDFProcessor:
    """Handles PDF text extraction and processing"""
    
    @staticmethod
    def extract_text_from_pdf(pdf_path: str) -> str:
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
    
    @staticmethod
    def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
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
    
    @staticmethod
    def get_pdf_files(directory: str) -> List[Path]:
        """
        Get all PDF files from a directory
        
        Args:
            directory: Directory path containing PDF files
            
        Returns:
            List of PDF file paths
        """
        pdf_dir = Path(directory)
        if not pdf_dir.exists():
            raise FileNotFoundError(f"Directory {directory} not found")
        
        return list(pdf_dir.glob("*.pdf"))
# main.py
# Main entry point for the HR Document Vectorization System

import logging
from pdf_vectorization import PDFVectorization

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """
    Main function to run the HR Document Vectorization System
    """
    print("=== HR Document Vectorization System ===")
    print("Now using all-mpnet-base-v2 for better HR document understanding")
    print()
    
    try:
        # Initialize the system
        system = PDFVectorization()
        
        # Load or create vectors
        success = system.load_or_create_vectors()
        if not success:
            print("Failed to load or create vectors")
            return
        
        # Test the system performance
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
            results = system.search(query, top_k=3)
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
            results = system.search(query, top_k=2)
            
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
        print("system.compare_models()")
        
        return system
        
    except Exception as e:
        logger.error(f"Error in main: {e}")
        return None

if __name__ == "__main__":
    system = main()
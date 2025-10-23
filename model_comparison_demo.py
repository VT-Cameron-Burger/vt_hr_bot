# model_comparison_demo.py
# Demo script to compare model performance

from load_data import load_data
from model_comparison import ModelComparison
import time

def compare_models_demo():
    """
    Demonstrate the difference between models
    """
    print("=== Model Comparison Demo ===\n")
    
    # Load the vectorization system with existing vectors
    system = load_data()
    if not system:
        print("No existing vectors found. Please run load_data.py first.")
        return
    
    print("Loaded existing vectors (all-mpnet-base-v2)\n")
    
    # Test queries specific to HR domain
    test_queries = [
        "employee benefits package",
        "vacation and sick leave",
        "performance evaluation criteria", 
        "workplace harassment reporting",
        "retirement savings plan"
    ]
    
    print("Testing current model (all-mpnet-base-v2):")
    print("-" * 50)
    
    total_time = 0
    similarities = []
    
    for query in test_queries:
        start_time = time.time()
        results = system.search(query, top_k=3)
        end_time = time.time()
        
        search_time = end_time - start_time
        total_time += search_time
        
        if results:
            similarities.append(results[0]["similarity_score"])
            print(f"\nQuery: '{query}'")
            print(f"Best match: {results[0]['metadata']['source_file']}")
            print(f"Similarity: {results[0]['similarity_score']:.4f}")
            print(f"Search time: {search_time:.3f}s")
            print(f"Preview: {results[0]['document'][:120]}...")
    
    avg_similarity = sum(similarities) / len(similarities) if similarities else 0
    avg_time = total_time / len(test_queries)
    
    print("\n" + "=" * 60)
    print("PERFORMANCE SUMMARY:")
    print(f"Average similarity score: {avg_similarity:.4f}")
    print(f"Average search time: {avg_time:.3f}s")
    print(f"Total search time: {total_time:.3f}s")
    
    print("\n" + "=" * 60)
    print("MODEL COMPARISON:")
    print("\nall-mpnet-base-v2 (CURRENT):")
    print("✓ 768-dimensional embeddings")
    print("✓ Better semantic understanding")
    print("✓ Optimized for professional documents")
    print("✓ Higher accuracy for HR/policy content")
    print("- Slower inference (~5-10s for full vectorization)")
    
    print("\nall-MiniLM-L6-v2 (PREVIOUS):")
    print("✓ 384-dimensional embeddings") 
    print("✓ Faster inference")
    print("✓ Good for general purpose")
    print("- Lower accuracy for specialized content")
    print("- Less context understanding")
    
    print("\nRECOMMENDATE USAGE:")
    print("- Use all-mpnet-base-v2 for HR bot (current choice)")
    print("- Use multi-qa-mpnet-base-dot-v1 if primarily Q&A")
    print("- Use all-MiniLM-L6-v2 if speed is critical")
    
    print("\n" + "=" * 60)
    print("MODEL COMPARISON AVAILABLE:")
    print("To compare different models, run:")
    print("  system.compare_models()")
    print("This will test multiple embedding models on HR queries")

if __name__ == "__main__":
    compare_models_demo()
# model_comparison.py
# Utilities for comparing different embedding models

import logging
from typing import List, Dict, Any, Optional

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    print("sentence-transformers not found. Install with: pip install sentence-transformers")
    SentenceTransformer = None

from vectorizer import DocumentVectorizer

logger = logging.getLogger(__name__)

class ModelComparison:
    """Utilities for comparing embedding model performance"""
    
    def __init__(self, vectorizer: DocumentVectorizer):
        """
        Initialize with an existing vectorizer that has loaded documents
        
        Args:
            vectorizer: DocumentVectorizer with loaded embeddings
        """
        self.vectorizer = vectorizer
    
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
        original_model = self.vectorizer.model
        original_model_name = self.vectorizer.model_name
        
        for model_name in model_names:
            print(f"\nTesting model: {model_name}")
            try:
                # Load model
                self.vectorizer.model = SentenceTransformer(model_name)
                self.vectorizer.model_name = model_name
                
                model_results = []
                for query in test_queries:
                    similar_docs = self.vectorizer.find_similar_documents(query, top_k=3)
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
        self.vectorizer.model = original_model
        self.vectorizer.model_name = original_model_name
        return results
    
    @staticmethod
    def print_comparison_results(results: Dict[str, Any]):
        """
        Print formatted comparison results
        
        Args:
            results: Results from compare_models()
        """
        print("\n" + "="*60)
        print("MODEL COMPARISON RESULTS")
        print("="*60)
        
        for model_name, result in results.items():
            if "error" in result:
                print(f"\n{model_name}: ERROR - {result['error']}")
                continue
                
            print(f"\n{model_name}:")
            print(f"  Average Similarity: {result['avg_top_similarity']:.4f}")
            
            print("  Sample Results:")
            for i, query_result in enumerate(result['results'][:2]):  # Show first 2 queries
                query = query_result['query']
                top_sim = query_result['top_similarity']
                if query_result['results']:
                    source = query_result['results'][0]['metadata']['source_file']
                    print(f"    '{query}' → {source} ({top_sim:.4f})")
    
    @staticmethod
    def get_hr_test_queries() -> List[str]:
        """
        Get a standard set of HR-related test queries
        
        Returns:
            List of HR test queries
        """
        return [
            "employee benefits and compensation",
            "vacation leave policy", 
            "performance evaluation process",
            "workplace harassment policy",
            "retirement plans and 401k",
            "employee training and development"
        ]
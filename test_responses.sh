#!/usr/bin/env bash
# test_response_quality.py - Test the improved response generation

source .venv/bin/activate

echo "🧪 Testing improved response generation..."
echo "=========================================="

python -c "
import sys, os
sys.path.append('ui')
from server import HRBotHandler
import load_data

# Create a mock handler to test the answer generation
class MockHandler(HRBotHandler):
    def __init__(self):
        self.vectorizer = load_data.load_data()

handler = MockHandler()

test_queries = [
    'gift matching',
    'employee benefits', 
    'vacation time',
    'dress code',
    'performance review'
]

for query in test_queries:
    print(f'\n=== QUERY: \"{query}\" ===')
    results = handler.vectorizer.search(query, top_k=2)
    if results:
        print(f'Similarity: {results[0][\"similarity_score\"]:.1%}')
        answer = handler.generate_answer(query, results)
        print(f'Response length: {len(answer)} chars')
        print('Response preview:')
        preview = answer[:200] + '...' if len(answer) > 200 else answer
        print(preview)
    else:
        print('No results found')
    print('-' * 50)
"

echo ""
echo "✅ Response quality test complete!"
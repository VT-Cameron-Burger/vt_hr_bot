# server.py
# Simple HTTP server to serve the UI and handle API requests

import os
import sys
import json
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs
import threading
import uuid
import webbrowser
from pathlib import Path

# Add parent directory to path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from load_data import load_data
from llm import LLMResponder

logger = logging.getLogger(__name__)

class HRBotHandler(BaseHTTPRequestHandler):
    """HTTP request handler for the HR Bot server"""
    
    def __init__(self, *args, vectorizer=None, **kwargs):
        self.vectorizer = vectorizer
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests for static files and API endpoints"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # Handle API endpoints
        if path == '/api/status':
            self.handle_status()
            return
        
        if path == '/':
            path = '/index.html'
        
        # Get the directory where server.py is located
        server_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(server_dir, path.lstrip('/'))
        
        try:
            if os.path.exists(file_path):
                # Determine content type
                content_type = self.get_content_type(file_path)
                
                # Read and serve file
                with open(file_path, 'rb') as f:
                    content = f.read()
                
                self.send_response(200)
                self.send_header('Content-Type', content_type)
                self.send_header('Content-Length', str(len(content)))
                self.end_headers()
                self.wfile.write(content)
            else:
                self.send_error(404, 'File not found')
                
        except Exception as e:
            logger.error(f"Error serving file {file_path}: {e}")
            self.send_error(500, 'Internal server error')
    
    def do_POST(self):
        """Handle POST requests for API endpoints"""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/api/query':
            self.handle_query()
        elif parsed_path.path == '/api/status':
            self.handle_status()
        else:
            self.send_error(404, 'API endpoint not found')
    
    def handle_query(self):
        """Handle HR query requests"""
        try:
            # Parse request body
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            query = data.get('query', '').strip()
            if not query:
                self.send_json_response({'error': 'No query provided'}, 400)
                return
            
            if not self.vectorizer:
                self.send_json_response({'error': 'HR system not initialized'}, 503)
                return
            
            # Create a unique request id for tracing/cost-logging
            request_id = uuid.uuid4().hex

            # Search for similar documents
            results = self.vectorizer.search(query, top_k=3)
            
            if results:
                # Generate response based on top results
                top_result = results[0]
                answer = self.generate_answer(query, results, request_id=request_id)
                sources = [r['metadata']['source_file'] for r in results]
                
                response = {
                    'answer': answer,
                    'sources': sources,
                    'confidence': top_result['similarity_score'],
                    'request_id': request_id,
                    'query': query
                }
            else:
                response = {
                    'answer': 'I could not find relevant information for your query. Please try rephrasing or contact HR directly.',
                    'sources': [],
                    'confidence': 0.0,
                    'query': query
                }
            
            self.send_json_response(response)
            
        except Exception as e:
            logger.error(f"Error handling query: {e}")
            self.send_json_response({'error': 'Failed to process query'}, 500)
    
    def handle_status(self):
        """Handle status check requests"""
        try:
            status = {
                'status': 'online' if self.vectorizer else 'offline',
                'documents_loaded': len(self.vectorizer.vectorizer.documents) if self.vectorizer else 0,
                'model': 'all-mpnet-base-v2'
            }
            self.send_json_response(status)
            
        except Exception as e:
            logger.error(f"Error getting status: {e}")
            self.send_json_response({'error': 'Failed to get status'}, 500)
    
    def generate_answer(self, query, results, request_id: str = None):
        """Generate a human-readable answer from search results.

        If an LLM is attached to the handler (self.llm), prefer using it to
        synthesize an answer from the top results. Otherwise fall back to the
        original rule-based summarization/preview logic.
        """
        if not results:
            return "I couldn't find relevant information for your query. Please try rephrasing your question or contact HR directly."

        # If an LLM is available, use it to generate a response from the top results
        try:
            if hasattr(self, 'llm') and self.llm is not None:
                # Let the LLM synthesize an answer from the returned chunks
                # Use slightly more generous generation parameters for helpful answers
                llm_answer = self.llm.generate(
                    query,
                    results,
                    max_new_tokens=200,
                    do_sample=True,
                    temperature=0.3,
                    top_p=0.95,
                    num_beams=2,
                    request_id=request_id,
                )
                # If the LLM produced something reasonable, return it
                if llm_answer and len(llm_answer.strip()) > 5:
                    return llm_answer
        except Exception as e:
            # On any LLM failure, log and fall back to rule-based answer
            logger = logging.getLogger(__name__)
            logger.warning(f"LLM generation failed: {e}. Falling back to rule-based answer.")

        # Rule-based fallback (existing behavior)
        top_result = results[0]
        document = top_result['document']
        source_file = top_result['metadata']['source_file']
        similarity = top_result['similarity_score']

        # If similarity is very low, provide a more cautious response
        if similarity < 0.3:
            answer = f"I found some potentially relevant information in {source_file}, but the match isn't very strong (similarity: {similarity:.1%}). You may want to review the full document or contact HR for more specific guidance."
            if len(results) > 1:
                other_sources = [r['metadata']['source_file'] for r in results[1:]]
                unique_sources = list(dict.fromkeys(other_sources))
                if unique_sources:
                    answer += f"\n\nOther potentially relevant documents: {', '.join(unique_sources)}"
            return answer

        # Clean the document text first
        cleaned_document = self.clean_text(document)

        # Try to extract relevant sentences
        sentences = self.extract_relevant_sentences(cleaned_document, query)

        if sentences and len(sentences) > 100:  # Only use if we got meaningful content
            answer = f"Based on {source_file}:\n\n{sentences}"
        else:
            # Fallback: provide a summary with document reference
            preview = self.get_clean_preview(cleaned_document, max_length=200)
            answer = f"I found relevant information in {source_file}. Here's a preview:\n\n{preview}\n\n**Note**: Due to document formatting, please refer to the original {source_file} for complete and accurate information."

        # Add other sources
        if len(results) > 1:
            other_sources = [r['metadata']['source_file'] for r in results[1:]]
            unique_sources = list(dict.fromkeys(other_sources))  # Remove duplicates
            if unique_sources:
                answer += f"\n\nAdditional relevant documents: {', '.join(unique_sources)}"

        return answer
    
    def get_clean_preview(self, text, max_length=200):
        """Get a clean preview of text with complete words"""
        if not text or len(text) <= max_length:
            return text
        
        # Find a good break point near max_length
        preview = text[:max_length]
        last_space = preview.rfind(' ')
        last_period = preview.rfind('.')
        
        if last_period > max_length * 0.7:  # If there's a period in the last 30%
            return text[:last_period + 1]
        elif last_space > max_length * 0.8:  # If there's a space in the last 20%
            return text[:last_space] + "..."
        else:
            return preview + "..."
    
    def clean_text(self, text):
        """Clean and normalize text for better readability"""
        import re
        
        if not text:
            return ""
        
        # Replace multiple whitespace with single spaces
        text = re.sub(r'\s+', ' ', text)
        
        # Fix common PDF extraction issues
        text = re.sub(r'([a-z])([A-Z])', r'\1. \2', text)  # Add periods between sentences
        text = re.sub(r'([.!?])\s*([a-z])', lambda m: m.group(1) + ' ' + m.group(2).upper(), text)  # Capitalize after periods
        
        # Remove excessive line breaks and normalize spacing
        text = re.sub(r'\n\s*\n', '. ', text)
        text = re.sub(r'\n', ' ', text)
        
        # Clean up multiple periods
        text = re.sub(r'\.{2,}', '.', text)
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def extract_relevant_sentences(self, document, query, max_sentences=3):
        """Extract sentences that are most relevant to the query"""
        import re
        
        # Split into sentences more carefully
        sentences = re.split(r'[.!?]+(?:\s+|$)', document)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 30]  # Longer minimum for quality
        
        if not sentences:
            return ""
        
        # Find sentences containing query words
        query_words = [word.lower() for word in query.split() if len(word) > 2]  # Skip short words
        relevant_sentences = []
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            # Count how many query words appear in this sentence
            word_matches = sum(1 for word in query_words if word in sentence_lower)
            if word_matches > 0:
                # Clean the sentence
                cleaned_sentence = self.clean_sentence(sentence)
                if len(cleaned_sentence) > 50:  # Ensure meaningful content
                    relevant_sentences.append((cleaned_sentence, word_matches))
        
        if relevant_sentences:
            # Sort by relevance and take top sentences
            relevant_sentences.sort(key=lambda x: x[1], reverse=True)
            selected = [s[0] for s in relevant_sentences[:max_sentences]]
            return '. '.join(selected) + '.'
        
        return ""
    
    def clean_sentence(self, sentence):
        """Clean a single sentence for better readability"""
        import re
        
        # Remove leading/trailing whitespace
        sentence = sentence.strip()
        
        # Fix common PDF artifacts
        sentence = re.sub(r'\s+', ' ', sentence)  # Multiple spaces to single
        sentence = re.sub(r'([a-z])\s+([A-Z])', r'\1. \2', sentence)  # Missing periods
        
        # Remove partial words at the beginning (PDF extraction artifacts)
        if len(sentence) > 10:
            words = sentence.split()
            if len(words) > 1 and len(words[0]) < 4 and not words[0][0].isupper():
                sentence = ' '.join(words[1:])
        
        # Ensure proper capitalization
        if sentence and not sentence[0].isupper():
            sentence = sentence[0].upper() + sentence[1:]
            
        return sentence
    
    def get_complete_sentences(self, document, max_length=400):
        """Get complete sentences from the beginning of the document"""
        import re
        
        sentences = re.split(r'[.!?]+', document)
        result = ""
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 20:  # Skip very short fragments
                continue
                
            if len(result) + len(sentence) + 2 <= max_length:
                if result:
                    result += ". " + sentence
                else:
                    result = sentence
            else:
                break
        
        if result and not result.endswith('.'):
            result += '.'
            
        return result if result else document[:max_length] + "..."
    
    def send_json_response(self, data, status=200):
        """Send JSON response"""
        response = json.dumps(data, indent=2)
        
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Content-Length', str(len(response)))
        self.end_headers()
        self.wfile.write(response.encode('utf-8'))
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def get_content_type(self, file_path):
        """Determine content type based on file extension"""
        ext = os.path.splitext(file_path)[1].lower()
        
        content_types = {
            '.html': 'text/html',
            '.css': 'text/css',
            '.js': 'application/javascript',
            '.json': 'application/json',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.svg': 'image/svg+xml',
            '.ico': 'image/x-icon'
        }
        
        return content_types.get(ext, 'application/octet-stream')
    
    def log_message(self, format, *args):
        """Override to use our logger"""
        logger.info(f"{self.address_string()} - {format % args}")

def create_handler(vectorizer, llm=None):
    """Create a handler class with the vectorizer and optional llm injected"""
    class HandlerWithVectorizer(HRBotHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, vectorizer=vectorizer, **kwargs)
            # attach LLM if provided
            self.llm = llm
    return HandlerWithVectorizer

def start_server(port=8000, auto_open=True):
    """Start the HR Bot web server"""
    
    print("🤖 Starting VT HR Bot Server...")
    print("=" * 50)
    
    # Load the vectorization system
    print("Loading HR document database...")
    try:
        vectorizer = load_data()
        if not vectorizer:
            print("❌ Failed to load HR database")
            return
        
        print(f"✅ Loaded {len(vectorizer.vectorizer.documents)} document chunks")
        
    except Exception as e:
        print(f"❌ Error loading HR database: {e}")
        return
    
    # Create LLM responder (small local model for development)
    try:
        llm = LLMResponder(model_name="google/flan-t5-small")
    except Exception as e:
        print(f"⚠️  Could not create LLMResponder: {e}. Continuing without LLM.")
        llm = None

    # Create server
    handler_class = create_handler(vectorizer, llm=llm)
    server = HTTPServer(('localhost', port), handler_class)
    
    print(f"🚀 Server starting on http://localhost:{port}")
    print("Press Ctrl+C to stop the server")
    print("=" * 50)
    
    # Open browser
    if auto_open:
        def open_browser():
            import time
            time.sleep(1)  # Give server time to start
            webbrowser.open(f'http://localhost:{port}')
        
        threading.Thread(target=open_browser, daemon=True).start()
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down server...")
        server.shutdown()
        print("✅ Server stopped")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='VT HR Bot Web Server')
    parser.add_argument('--port', type=int, default=8000, help='Server port (default: 8000)')
    parser.add_argument('--no-browser', action='store_true', help='Don\'t automatically open browser')
    
    args = parser.parse_args()
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    start_server(args.port, not args.no_browser)
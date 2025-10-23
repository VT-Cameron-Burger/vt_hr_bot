# VT HR Bot Web Interface

A modern, responsive web interface for the Virginia Tech HR chatbot system.

## Features

- **Clean, Modern UI** - Built with pure HTML, CSS, and JavaScript
- **Responsive Design** - Works on desktop, tablet, and mobile devices
- **Real-time Chat** - Interactive chat interface with typing indicators
- **VT Branding** - Uses Virginia Tech colors and styling
- **Quick Suggestions** - Pre-defined buttons for common HR topics
- **Source Attribution** - Shows which policy documents were referenced
- **Backend Integration** - Connects to Python vectorization system

## Files

- `index.html` - Main HTML structure
- `styles.css` - CSS styling with VT branding
- `script.js` - JavaScript chat functionality
- `server.py` - Python backend server

## Setup & Usage

### 1. Start the Server

From the main project directory:

```bash
# Activate virtual environment
source .venv/bin/activate

# Start the web server
python ui/server.py
```

The server will:
- Load the HR document database
- Start a web server on `http://localhost:8000`
- Automatically open your browser

### 2. Alternative Port

```bash
python ui/server.py --port 8080
```

### 3. No Auto-Browser

```bash
python ui/server.py --no-browser
```

## API Endpoints

### GET `/`
Serves the main web interface

### POST `/api/query`
Query the HR bot
```json
{
  "query": "What are the employee benefits?"
}
```

Response:
```json
{
  "answer": "Virginia Tech offers comprehensive benefits...",
  "sources": ["4245.pdf", "4040.pdf"],
  "confidence": 0.85,
  "query": "What are the employee benefits?"
}
```

### GET `/api/status`
Check system status
```json
{
  "status": "online",
  "documents_loaded": 3748,
  "model": "all-mpnet-base-v2"
}
```

## Design Features

### VT Branding
- **Primary Color**: VT Maroon (#861F41)
- **Secondary Color**: VT Orange (#CF4420)
- **Typography**: Inter font family
- **Professional styling** for university environment

### Responsive Layout
- **Desktop**: Full-width chat interface
- **Mobile**: Optimized for touch interaction
- **Accessibility**: Proper contrast and focus states

### Chat Experience
- **Message bubbles** with user/bot distinction
- **Typing indicators** for better UX
- **Smooth animations** for message appearance
- **Source citations** for transparency

## Customization

### Colors
Edit CSS variables in `styles.css`:
```css
:root {
    --primary-color: #861F41;    /* VT Maroon */
    --secondary-color: #CF4420;  /* VT Orange */
    /* ... */
}
```

### Suggestions
Edit the suggestion buttons in `index.html`:
```html
<button class="suggestion-btn" data-query="your query">
    🔍 Your Topic
</button>
```

### Backend Model
Change the embedding model in `server.py` or `load_data.py`

## Development

### Testing Locally
1. Make sure the vectorization system is working
2. Start the server: `python ui/server.py`
3. Open browser to `http://localhost:8000`
4. Test with various HR queries

### Adding Features
- **New API endpoints**: Add to `server.py`
- **UI enhancements**: Modify HTML/CSS/JS files
- **Additional models**: Integrate in the backend

### Debugging
- Check browser developer console for JavaScript errors
- Monitor server logs for backend issues
- Verify the vector database is loaded correctly
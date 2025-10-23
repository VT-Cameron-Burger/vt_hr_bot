# VT HR Bot - Quick Start Guide

## ✅ Your System is Ready!

Your VT HR Bot is set up and ready to use. All dependencies are installed and the vector database is built with 3,748 document chunks.

**🔧 Recent Improvements:**
- **Better response quality** - Fixed garbled text and incomplete sentences
- **Smarter answer generation** - Responses now include document context and quality checks  
- **Enhanced text cleaning** - Improved handling of PDF extraction artifacts

## 🚀 Starting the Server

### Method 1: Use the Run Script (Recommended)
```bash
./scripts/run_server.sh
```

### Method 2: Manual Start
```bash
# From the project root
source .venv/bin/activate
python ui/server.py --port 8000
```

## 🌐 Accessing the UI

Once the server starts, you'll see:
```
🚀 Server starting on http://localhost:8000
✅ Loaded 3748 document chunks
```

**On WSL (your setup):**
1. Open your Windows browser
2. Navigate to: `http://localhost:8000`

**Note:** The server may show WSL interop warnings - these are harmless. The server will still work perfectly.

## 🔧 Using the UI

The web interface provides:
- **Status indicator** - Shows if the system is online
- **Suggestion buttons** - Quick queries about common HR topics
- **Search box** - Ask any HR-related question
- **Sources** - See which PDFs contain the answers

## 💬 Example Queries

Try these sample questions:
- "What are the employee benefits?"
- "How do I request time off?"
- "What is the dress code policy?"
- "How does the performance review process work?"
- "Gift matching policy"

## 🛑 Stopping the Server

Press `Ctrl+C` in the terminal where the server is running.

## 🧪 Testing

Test response quality:
```bash
./test_responses.sh
```

Test the API:
```bash
./test_api.sh
```

## 📁 Files and Directories

- `pdf_vectors.pkl` - Your vector database (15.4MB)
- `downloaded_pdfs/` - Source PDF documents (186 files)
- `scripts/run_server.sh` - Convenient startup script
- `ui/` - Web interface files
- `test_responses.sh` - Test response quality
- `test_api.sh` - Test server API

## 🔍 Quick Testing

Test the system without the UI:
```bash
source .venv/bin/activate
python -c "
import load_data
system = load_data.load_data()
results = system.search('employee benefits', top_k=3)
for r in results:
    print(f'- {r[\"metadata\"][\"source_file\"]}: {r[\"similarity_score\"]:.1%}')
"
```

## 🚨 Troubleshooting

**Server won't start:**
- Make sure you're in the project directory
- Ensure `.venv` is activated: `source .venv/bin/activate`
- Check if port 8000 is already in use: `./scripts/run_server.sh 8001`

**UI shows "Offline":**
- Check if the server is running and shows "✅ Loaded 3748 document chunks"
- Try refreshing the browser page

**Poor response quality:**
- The system works best with specific HR-related queries
- Try rephrasing questions to be more specific
- For policy details, refer to the source document mentioned in responses

**WSL browser issues:**
- Open `http://localhost:8000` manually in Windows browser
- The server works fine even with WSL interop warnings

---

**Your system is fully operational with improved response quality! 🎉**
#!/usr/bin/env bash
# Quick test of the server API

echo "🧪 Testing Server API..."
echo "========================"

# Check if server is running
if ! curl -s http://localhost:8000/api/status > /dev/null 2>&1; then
    echo "⚠️  Server not running on port 8000. Starting server..."
    source .venv/bin/activate
    python ui/server.py --port 8000 &
    SERVER_PID=$!
    echo "🔄 Waiting for server to start..."
    sleep 8
else
    echo "✅ Server is already running"
fi

echo ""
echo "📊 Server Status:"
curl -s http://localhost:8000/api/status | jq

echo ""
echo "💬 Test Query: 'employee benefits'"
curl -s -X POST -H "Content-Type: application/json" \
     -d '{"query": "employee benefits"}' \
     http://localhost:8000/api/query | jq -r '.answer'

echo ""
echo "💬 Test Query: 'gift matching'"
curl -s -X POST -H "Content-Type: application/json" \
     -d '{"query": "gift matching"}' \
     http://localhost:8000/api/query | jq -r '.answer'

echo ""
echo "✅ API test complete!"

# Clean up if we started the server
if [ ! -z "$SERVER_PID" ]; then
    echo "🛑 Stopping test server..."
    kill $SERVER_PID 2>/dev/null || true
fi
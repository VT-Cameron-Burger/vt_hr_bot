#!/usr/bin/env python3
# test_ui.py
# Quick test script to validate the UI system

import sys
import os
import requests
import time
import subprocess
import signal
from threading import Thread

def start_server():
    """Start the server in background"""
    try:
        # Change to project directory
        os.chdir('/home/cameronburger/vt_hr_bot')
        
        # Start server
        cmd = ['python', 'ui/server.py', '--port', '8081', '--no-browser']
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        
        print("🚀 Starting server...")
        
        # Wait for server to start
        time.sleep(5)
        
        return process
        
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        return None

def test_api():
    """Test the API endpoints"""
    base_url = "http://localhost:8081"
    
    try:
        # Test status endpoint
        print("📡 Testing status endpoint...")
        response = requests.get(f"{base_url}/api/status", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {data['status']}")
            print(f"📄 Documents: {data['documents_loaded']}")
            print(f"🤖 Model: {data['model']}")
        else:
            print(f"❌ Status check failed: {response.status_code}")
            return False
        
        # Test query endpoint
        print("\n💬 Testing query endpoint...")
        query_data = {"query": "employee benefits"}
        response = requests.post(f"{base_url}/api/query", json=query_data, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Query successful")
            print(f"📝 Answer length: {len(data['answer'])} characters")
            print(f"📚 Sources: {', '.join(data['sources'])}")
            print(f"🎯 Confidence: {data['confidence']:.3f}")
            print(f"💡 Preview: {data['answer'][:100]}...")
        else:
            print(f"❌ Query failed: {response.status_code}")
            return False
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ API test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 VT HR Bot UI Test Suite")
    print("=" * 40)
    
    # Start server
    server_process = start_server()
    if not server_process:
        return False
    
    try:
        # Test API
        success = test_api()
        
        if success:
            print("\n" + "=" * 40)
            print("🎉 All tests passed!")
            print(f"🌐 Web interface: http://localhost:8081")
            print("💡 You can now access the HR bot web interface")
        else:
            print("\n❌ Some tests failed")
            
    finally:
        # Clean up
        print("\n🛑 Stopping server...")
        server_process.terminate()
        server_process.wait(timeout=5)
        print("✅ Server stopped")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
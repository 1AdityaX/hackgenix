#!/usr/bin/env python3
"""
Simple test script to verify the agentic RAG server is working
"""
import requests
import json

def test_agentic_rag():
    """Test the agentic RAG server with a sample query"""
    try:
        # Test query
        query = "What are my classes today?"
        url = f"http://localhost:8000/?query={query}"
        
        print(f"Testing query: {query}")
        print(f"URL: {url}")
        
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Server responded successfully!")
            print(f"Response: {json.dumps(data, indent=2)}")
        else:
            print(f"❌ Server returned status code: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure the server is running on localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_agentic_rag()

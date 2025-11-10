#!/usr/bin/env python3
"""
Simple test to check if Ollama is working
"""

import requests
import json

def test_ollama():
    base_url = "http://localhost:11434"
    
    try:
        # Test if Ollama is running
        print("Testing Ollama connection...")
        response = requests.get(f"{base_url}/api/tags", timeout=5)
        response.raise_for_status()
        models = response.json()
        print(f"✅ Ollama is running! Available models: {[m['name'] for m in models.get('models', [])]}")
        
        # Test a simple generation
        print("\nTesting model generation...")
        payload = {
            "model": "llama3.3:70b",
            "prompt": "Say hello in one word.",
            "stream": False,
            "options": {
                "temperature": 0.1,
                "num_predict": 10
            }
        }
        
        response = requests.post(f"{base_url}/api/generate", json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        response_text = result.get('response', '').strip()
        print(f"✅ Model response: '{response_text}'")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Ollama. Is it running? Try: ollama serve")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_ollama()

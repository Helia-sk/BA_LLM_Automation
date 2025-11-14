#!/usr/bin/env python3
"""
Check available models for your API keys
"""

import json
import openai
from anthropic import Anthropic

def check_openai_models(api_key):
    """Check available OpenAI models"""
    print("🔍 Checking OpenAI models...")
    try:
        client = openai.OpenAI(api_key=api_key)
        
        # Test with a simple request to see what models work
        test_models = [
            "gpt-4o",
            "gpt-4o-mini", 
            "gpt-4-turbo",
            "gpt-4",
            "gpt-3.5-turbo"
        ]
        
        working_models = []
        
        for model in test_models:
            try:
                print(f"  Testing {model}...", end=" ")
                response = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": "Hello"}],
                    max_tokens=5
                )
                print("✅ Working")
                working_models.append(model)
            except Exception as e:
                print(f"❌ Error: {str(e)[:50]}...")
        
        return working_models
        
    except Exception as e:
        print(f"❌ OpenAI API Error: {str(e)}")
        return []

def check_anthropic_models(api_key):
    """Check available Anthropic models"""
    print("\n🔍 Checking Anthropic models...")
    try:
        client = Anthropic(api_key=api_key)
        
        test_models = [
            "claude-3-5-sonnet-20241022",
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229", 
            "claude-3-haiku-20240307"
        ]
        
        working_models = []
        
        for model in test_models:
            try:
                print(f"  Testing {model}...", end=" ")
                response = client.messages.create(
                    model=model,
                    max_tokens=5,
                    messages=[{"role": "user", "content": "Hello"}]
                )
                print("✅ Working")
                working_models.append(model)
            except Exception as e:
                print(f"❌ Error: {str(e)[:50]}...")
        
        return working_models
        
    except Exception as e:
        print(f"❌ Anthropic API Error: {str(e)}")
        return []

def main():
    print("🤖 Model Availability Checker")
    print("=" * 40)
    
    # Load config
    try:
        with open("config.json", 'r') as f:
            config = json.load(f)
    except Exception as e:
        print(f"Error loading config.json: {e}")
        return
    
    openai_key = config.get('openai_api_key', '')
    anthropic_key = config.get('anthropic_api_key', '')
    
    if not openai_key and not anthropic_key:
        print("❌ No API keys found in config.json")
        return
    
    all_working_models = []
    
    # Check OpenAI models
    if openai_key and openai_key != "your-openai-api-key-here":
        openai_models = check_openai_models(openai_key)
        all_working_models.extend(openai_models)
    else:
        print("⚠️  OpenAI API key not configured or using placeholder")
    
    # Check Anthropic models  
    if anthropic_key and anthropic_key != "your-anthropic-api-key-here" and anthropic_key != "null":
        anthropic_models = check_anthropic_models(anthropic_key)
        all_working_models.extend(anthropic_models)
    else:
        print("⚠️  Anthropic API key not configured or using placeholder")
    
    # Check local models
    print("\n🔍 Checking local models...")
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code == 200:
            data = response.json()
            local_models = data.get('models', [])
            if local_models:
                print("✅ Local Ollama models available:")
                for model in local_models:
                    model_name = model.get('name', 'Unknown')
                    print(f"  📦 local:{model_name}")
                    all_working_models.append(f"local:{model_name}")
            else:
                print("⚠️  No local models found (install with: ollama pull llama2)")
        else:
            print("⚠️  Ollama not running (start with: ollama serve)")
    except:
        print("⚠️  Ollama not available (install Ollama and run: ollama serve)")
    
    # Summary
    print("\n" + "=" * 40)
    print("📋 SUMMARY - Available Models:")
    print("=" * 40)
    
    if all_working_models:
        for i, model in enumerate(all_working_models, 1):
            print(f"{i:2}. {model}")
        
        print(f"\n✅ Total: {len(all_working_models)} models available")
        print("\n💡 To use a model, change the 'model' field in config.json")
        print("   Example: \"model\": \"gpt-4o-mini\"")
    else:
        print("❌ No working models found")
        print("   Check your API keys and internet connection")

if __name__ == "__main__":
    main()

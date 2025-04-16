import requests
import json

print("Checking available Ollama models...")
try:
    response = requests.get("http://localhost:11434/api/tags")
    if response.status_code == 200:
        models = response.json().get("models", [])
        print(f"Found {len(models)} models:")
        for model in models:
            print(f"- {model.get('name')} (Size: {model.get('size')/(1024*1024*1024):.1f} GB)")
    else:
        print(f"Error: {response.status_code} - {response.text}")
except Exception as e:
    print(f"Error connecting to Ollama: {str(e)}")

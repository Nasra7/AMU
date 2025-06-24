import requests
import sys
import subprocess
import time

# Models needed for the application
REQUIRED_MODELS = ["llama3.2", "qwen2.5"]

def check_ollama_running():
    """Check if Ollama service is running"""
    try:
        response = requests.get("http://localhost:11434/api/tags")
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        return False

def get_available_models():
    """Get list of available models in Ollama"""
    try:
        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code == 200:
            data = response.json()
            return [model.get("name") for model in data.get("models", [])]
        return []
    except requests.exceptions.ConnectionError:
        return []

def download_missing_models():
    """Download any missing required models"""
    available_models = get_available_models()
    
    for model in REQUIRED_MODELS:
        if model not in available_models:
            print(f"Model '{model}' is not installed. Downloading now...")
            try:
                subprocess.run(["ollama", "pull", model], check=True)
                print(f"Successfully downloaded {model}")
            except subprocess.CalledProcessError as e:
                print(f"Failed to download {model}: {str(e)}")
                print(f"Please download manually with: ollama pull {model}")
        else:
            print(f"Model '{model}' is already installed.")

def main():
    """Main function"""
    print("Checking Ollama service and model availability...")
    
    if not check_ollama_running():
        print("ERROR: Ollama service is not running!")
        print("Please start Ollama with 'ollama serve' command")
        return 1
    
    print("Ollama service is running.")
    download_missing_models()
    
    available_models = get_available_models()
    all_required_available = all(model in available_models for model in REQUIRED_MODELS)
    
    if all_required_available:
        print("\nAll required models are available! Your application should work properly.")
    else:
        missing = [model for model in REQUIRED_MODELS if model not in available_models]
        print(f"\nWARNING: The following models are still missing: {', '.join(missing)}")
        print("Your application may fall back to using only the default model.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
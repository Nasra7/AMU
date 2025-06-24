# from elevenlabs import stream
# from elevenlabs.client import ElevenLabs

# # Create the client with your API key
# client = ElevenLabs(
#   api_key='sk_82c5a3ce0a27b87375ff16b7a56b562f3288a8934321b9f9'
# )

# # Test text-to-speech streaming
# audio_stream = client.text_to_speech.convert_as_stream(
#     text="This is a test of ElevenLabs API integration with Ollama",
#     voice_id="2EiwWnXFnvU5JabPnv8n",
#     #voice_id="21m00Tcm4TlvDq8ikWAM",  # You'll need a valid voice ID
#     model_id="eleven_multilingual_v2"
# )

# # Play the audio to test
# stream(audio_stream)

import json
import requests
import asyncio
import aiohttp
import sys

def print_encoding_info():
    """Print information about the system's default encoding"""
    print("\n=== Encoding Information ===")
    print(f"Default encoding: {sys.getdefaultencoding()}")
    print(f"stdout encoding: {sys.stdout.encoding}")
    print(f"stdin encoding: {sys.stdin.encoding}")
    print("===========================\n")

def test_turkish_chars():
    """Test handling of Turkish characters"""
    turkish_chars = "ığşçöüİĞŞÇÖÜ"
    print("Turkish characters:")
    print(turkish_chars)
    
    # Test encoding/decoding
    print("\nEncoding/decoding test:")
    encoded = turkish_chars.encode('utf-8')
    decoded = encoded.decode('utf-8')
    print(f"Original: {turkish_chars}")
    print(f"Encoded (bytes): {encoded}")
    print(f"Decoded back: {decoded}")
    print(f"Success: {turkish_chars == decoded}")

def test_json_handling():
    """Test handling Turkish characters in JSON"""
    test_data = {
        "message": "Merhaba, nasılsın? İşler yolunda mı?",
        "special_chars": "ığşçöüİĞŞÇÖÜ"
    }
    
    print("\n=== JSON Handling Test ===")
    # Encode to JSON
    json_str = json.dumps(test_data)
    print(f"JSON encoded: {json_str}")
    
    # Decode back from JSON
    decoded = json.loads(json_str)
    print(f"JSON decoded: {decoded}")
    
    # Check if data is preserved
    success = (test_data["message"] == decoded["message"] and 
               test_data["special_chars"] == decoded["special_chars"])
    print(f"JSON round-trip success: {success}")

async def test_api_call():
    """Test sending Turkish characters to Ollama API"""
    print("\n=== Ollama API Test with Turkish ===")
    
    turkish_text = "Merhaba, nasılsın? Bu bir test mesajıdır. İşler yolunda mı?"
    
    try:
        async with aiohttp.ClientSession() as session:
            # Try with both models
            for model in ["llama3.2:latest", "qwen2.5:1.5b"]:
                print(f"\nTesting with model: {model}")
                
                payload = {
                    "model": model,
                    "prompt": turkish_text,
                    "stream": False
                }
                
                print(f"Request payload: {json.dumps(payload)}")
                
                async with session.post("http://localhost:11434/api/generate", json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        response_text = result.get('response', '')
                        print(f"API response: {response_text}")
                    else:
                        error_text = await response.text()
                        print(f"API error: {response.status} - {error_text}")
    except Exception as e:
        print(f"API test error: {str(e)}")

def print_debug_suggestions():
    """Print debugging suggestions for Turkish character issues"""
    print("\n=== Debugging Suggestions ===")
    print("1. Check if all parts of your application use UTF-8 encoding")
    print("2. Make sure your frontend properly encodes Turkish characters when sending to backend")
    print("3. Check Network tab in browser DevTools to see if Turkish characters are being sent correctly")
    print("4. Look for specific error messages when Turkish characters are used")
    print("5. Consider adding error handling for language detection")
    print("6. Try bypassing the language detection and hardcode a test with the qwen model")
    print("==============================")

async def main():
    # Print encoding information
    print_encoding_info()
    
    # Test Turkish character handling
    test_turkish_chars()
    
    # Test JSON handling
    test_json_handling()
    
    # Test API call with Turkish
    await test_api_call()
    
    # Print debug suggestions
    print_debug_suggestions()

if __name__ == "__main__":
    asyncio.run(main())
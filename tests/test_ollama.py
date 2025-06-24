from langchain_community.chat_models import ChatOllama
import asyncio

async def test_ollama():
    try:
        # Initialize the chat model
        chat = ChatOllama(
            model="llama3.2",
            temperature=0.7,
        )
        
        # Test with a simple message
        response = await chat.ainvoke("Hello, are you working?")
        print("Response:", response)
        print("Test successful!")
        
    except Exception as e:
        print(f"Error testing Ollama: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_ollama())
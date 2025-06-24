# # terminal_chat.py
import asyncio
import os
import django
from asgiref.sync import sync_to_async

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AMU.settings')
django.setup()

from personality_profiles.models import PersonalityProfile
from agents.services.response_generator_agent import ResponseGeneratorAgent
from conversations.models import Conversation, Message

# Create sync_to_async versions of database operations
get_all_profiles = sync_to_async(lambda: list(PersonalityProfile.objects.all()))
create_conversation = sync_to_async(Conversation.objects.create)
create_message = sync_to_async(Message.objects.create)
save_conversation = sync_to_async(lambda x: x.save())
get_conversation_messages = sync_to_async(lambda conv: list(Message.objects.filter(conversation=conv).order_by('timestamp')))

async def display_profile_info(profile):
    """Display the character's information before starting chat"""
    print("\n" + "="*50)
    print(f"Character Profile: {profile.name}")
    print("="*50)
    print(f"Description: {profile.description}")
    print(f"Background: {profile.background_story}")
    print(f"Personality: {profile.personality_traits}")
    print(f"Speech Patterns: {profile.speech_patterns}")
    print("="*50 + "\n")

async def build_conversation_history(conversation):
    """Build a conversation history string from messages"""
    messages = await get_conversation_messages(conversation)
    history = ""
    
    for msg in messages:
        sender = "User" if msg.is_user else conversation.profile.name
        history += f"{sender}: {msg.content}\n"
    
    return history

async def chat_session():
    try:
        # Get and display available profiles
        profiles = await get_all_profiles()
        print("\nAvailable characters:")
        for idx, profile in enumerate(profiles, 1):
            print(f"{idx}. {profile.name}")
        
        # Let user choose a profile
        while True:
            try:
                choice = int(input("\nChoose a character number: "))
                if 1 <= choice <= len(profiles):
                    profile = profiles[choice-1]
                    break
                print("Invalid choice. Please try again.")
            except ValueError:
                print("Please enter a number.")
        
        # Display chosen profile info
        await display_profile_info(profile)
        
        # Create a new conversation
        conversation = await create_conversation(profile=profile)
        
        # Create response generator
        agent = ResponseGeneratorAgent(profile)
        
        print("Chat started! Type 'quit' to exit or 'info' to see character details again.\n")
        
        while True:
            # Get user input
            user_message = input("You: ").strip()
            
            if user_message.lower() == 'quit':
                break
            
            if user_message.lower() == 'info':
                await display_profile_info(profile)
                continue
            
            # Save user message
            await create_message(
                conversation=conversation,
                content=user_message,
                is_user=True
            )
            
            print(f"\n{profile.name} is typing...")
            
            try:
                # Build conversation history
                conversation_history = await build_conversation_history(conversation)
                
                # Generate response with full history context
                response_text, new_context = await agent.generate_response(
                    user_message,
                    conversation_history
                )
                
                await create_message(
                    conversation=conversation,
                    content=response_text,
                    is_user=False
                )
                
                # Update conversation context
                conversation.context = new_context
                await save_conversation(conversation)
                
                print(f"{profile.name}: {response_text}\n")
                
            except Exception as e:
                print(f"Error generating response: {str(e)}\n")
                
    except Exception as e:
        print(f"Unexpected error: {str(e)}")

if __name__ == "__main__":
    print("\nInitializing chat interface...")
    asyncio.run(chat_session())



# import asyncio
# import sys
# import re
# from urllib.parse import unquote

# # Import your services - you may need to adjust the import paths based on your project structure
# # We'll create a standalone WikipediaService here to avoid dependency issues
# import wikipediaapi

# class WikipediaService:
#     def __init__(self, user_agent="AMU-WikipediaReader/1.0"):
#         self.wiki = wikipediaapi.Wikipedia(
#             language='en',
#             extract_format=wikipediaapi.ExtractFormat.WIKI,
#             user_agent=user_agent
#         )
    
#     def get_page(self, title):
#         """Get a Wikipedia page by title."""
#         return self.wiki.page(title)
    
#     def get_summary(self, title):
#         """Get the summary of a Wikipedia page."""
#         page = self.get_page(title)
#         if page.exists():
#             return page.summary
#         return None
    
#     def get_full_content(self, title):
#         """Get the full content of a Wikipedia page."""
#         page = self.get_page(title)
#         if page.exists():
#             return page.text
#         return None
    
#     def get_sections(self, title):
#         """Get sections of a Wikipedia page as a dictionary."""
#         page = self.get_page(title)
#         sections = {}
#         if page.exists():
#             for section in page.sections:
#                 sections[section.title] = section.text
#         return sections
    
#     def search(self, query, max_results=10):
#         """Search Wikipedia for pages matching the query."""
#         # This requires the 'wikipedia' package
#         try:
#             import wikipedia
#             return wikipedia.search(query, results=max_results)
#         except ImportError:
#             print("Warning: 'wikipedia' package is required for search functionality")
#             return []

# class MockOllamaService:
#     """
#     A mock service to simulate LLM responses for terminal testing.
#     Replace this with your actual OllamaService when integrating.
#     """
#     async def generate_response(self, prompt):
#         print("\n[LLM Prompt that would be sent to Ollama]:")
#         print("-" * 50)
#         print(prompt[:200] + "..." if len(prompt) > 200 else prompt)
#         print("-" * 50)
        
#         # Simulate an LLM response
#         return """
# Factual Information Extracted:

# eh
# This factual information can be used to inform the character profile while personality traits will be derived from other sources.
# """

# class WikipediaTerminalTester:
#     def __init__(self):
#         self.wiki_service = WikipediaService()
#         self.ollama_service = MockOllamaService()
    
#     def extract_title_from_url(self, url):
#         """Extract the page title from a Wikipedia URL."""
#         # Match patterns like https://en.wikipedia.org/wiki/Character_name
#         pattern = r'wikipedia\.org/wiki/([^#?&]+)'
#         match = re.search(pattern, url)
#         if match:
#             # URL decode the title (convert %20 to spaces, etc.)
#             title = unquote(match.group(1))
#             # Replace underscores with spaces
#             title = title.replace('_', ' ')
#             return title
#         return None
    
#     async def process_url(self, url):
#         """Process a Wikipedia URL and extract information."""
#         title = self.extract_title_from_url(url)
        
#         if not title:
#             print(f"Error: Could not extract a valid Wikipedia page title from URL: {url}")
#             return
        
#         print(f"\nExtracting factual information for: {title}")
#         print("-" * 50)
        
#         # Get basic information
#         summary = self.wiki_service.get_summary(title)
#         if summary:
#             print("\n📝 SUMMARY:")
#             print("-" * 50)
#             print(summary[:300] + "..." if len(summary) > 300 else summary)
#         else:
#             print("\nNo summary found. The page might not exist or there might be an error.")
#             return
        
#         # Get all relevant sections for factual information
#         sections = self.wiki_service.get_sections(title)
#         factual_sections = [
#             'Biography', 'Early life', 'Career', 'Education', 'Works', 
#             'Filmography', 'Bibliography', 'Discography', 'Awards', 
#             'Personal life', 'Legacy', 'History', 'Background', 'Origins',
#             'Plot', 'Storyline', 'Publication history', 'Creation', 'Development'
#         ]
        
#         print("\n📑 FACTUAL SECTIONS:")
#         print("-" * 50)
#         found_sections = False
        
#         for section_name in factual_sections:
#             if section_name in sections:
#                 found_sections = True
#                 print(f"\n▶ {section_name}:")
#                 content = sections[section_name]
#                 print(content[:200] + "..." if len(content) > 200 else content)
        
#         if not found_sections:
#             print("No relevant factual sections found.")
        
#         # Extract and categorize factual information
#         print("\n🔍 FACTUAL INFORMATION EXTRACTION:")
#         print("-" * 50)
        
#         # Create task data
#         task_data = {
#             'subject_name': title,
#             'factual_data': {
#                 'name': title,
#                 'source': 'wikipedia',
#                 'summary': summary
#             }
#         }
        
#         # Add sections data
#         extracted_sections = {}
#         for section_name in factual_sections:
#             if section_name in sections:
#                 extracted_sections[section_name] = sections[section_name]
        
#         if extracted_sections:
#             task_data['factual_data']['extracted_sections'] = extracted_sections
        
#         # Generate factual extraction prompt
#         facts_prompt = f"""
#         Extract and categorize key factual information from the following Wikipedia data about {title}:
        
#         Summary: {summary[:500] if summary else "Not available"}
        
#         {"".join([f"{section}: {content[:300]}...\n" for section, content in extracted_sections.items()])}
        
#         Focus on:
#         1. Basic biographical/historical facts (dates, places, events)
#         2. Career or development milestones
#         3. Notable works, achievements, or contributions
#         4. Historical context and background
#         5. Factual relationships with other entities
        
#         Please organize this information into categories. Do NOT focus on personality traits, communication style, or subjective aspects.
#         Return ONLY factual information that can be used to build factual knowledge about this subject.
#         """
        
#         # Get simulated analysis
#         facts_analysis = await self.ollama_service.generate_response(facts_prompt)
#         print("\nFactual Information Extracted:")
#         print(facts_analysis)

#     async def interactive_loop(self):
#         """Run an interactive loop for the terminal tester."""
#         print("\n=== Wikipedia Factual Information Extractor ===")
#         print("Enter a Wikipedia URL to extract factual information or 'exit' to quit.")
        
#         while True:
#             try:
#                 print("\n" + "=" * 60)
#                 url = input("\nEnter Wikipedia URL (or 'exit'): ").strip()
                
#                 if url.lower() in ['exit', 'quit', 'q']:
#                     print("Exiting...")
#                     break
                
#                 if 'wikipedia.org' not in url:
#                     print("Please enter a valid Wikipedia URL.")
#                     continue
                
#                 await self.process_url(url)
                
#             except KeyboardInterrupt:
#                 print("\nExiting...")
#                 break
#             except Exception as e:
#                 print(f"Error: {str(e)}")
#                 import traceback
#                 traceback.print_exc()

# async def main():
#     tester = WikipediaTerminalTester()
#     await tester.interactive_loop()

# if __name__ == "__main__":
#     # Check Python version
#     if sys.version_info < (3, 7):
#         print("This script requires Python 3.7 or later.")
#         sys.exit(1)
    
#     try:
#         asyncio.run(main())
#     except KeyboardInterrupt:
#         print("\nProgram terminated by user.")
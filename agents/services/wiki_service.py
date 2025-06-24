# In file: Agents/Services/wikipedia_service.py
import wikipediaapi

class WikipediaService:
    def __init__(self, user_agent="AMU-WikipediaReader/1.0"):
        self.wiki = wikipediaapi.Wikipedia(
            language='en',
            extract_format=wikipediaapi.ExtractFormat.WIKI,
            user_agent=user_agent
        )
    
    def get_page(self, title):
        """Get a Wikipedia page by title."""
        return self.wiki.page(title)
    
    def get_summary(self, title):
        """Get the summary of a Wikipedia page."""
        page = self.get_page(title)
        if page.exists():
            return page.summary
        return None
    
    def get_full_content(self, title):
        """Get the full content of a Wikipedia page."""
        page = self.get_page(title)
        if page.exists():
            return page.text
        return None
    
    def get_sections(self, title):
        """Get sections of a Wikipedia page as a dictionary."""
        page = self.get_page(title)
        sections = {}
        if page.exists():
            for section in page.sections:
                sections[section.title] = section.text
        return sections
    
    def search(self, query, max_results=10):
        """Search Wikipedia for pages matching the query."""
        # This requires the 'wikipedia' package
        try:
            import wikipedia
            return wikipedia.search(query, results=max_results)
        except ImportError:
            print("Warning: 'wikipedia' package is required for search functionality")
            return []
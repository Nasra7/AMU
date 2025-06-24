from agents.services.wiki_service import WikipediaService

class WikipediaCollector:
    def __init__(self):
        self.wiki_service = WikipediaService()
    
    def enrich_profile(self, profile_data, character_name):
        """Add Wikipedia information to a profile."""
        summary = self.wiki_service.get_summary(character_name)
        if summary:
            profile_data['background']['wikipedia_summary'] = summary
            
        # You might want to extract specific sections relevant to personality
        sections = self.wiki_service.get_sections(character_name)
        relevant_sections = ['Personality', 'Character', 'Biography', 'Description']
        
        for section_name in relevant_sections:
            if section_name in sections:
                if 'traits' not in profile_data:
                    profile_data['traits'] = {}
                profile_data['traits'][f'wikipedia_{section_name.lower()}'] = sections[section_name]
        
        return profile_data
    
    def collect_character_data(self, character_name):
        """Collect all relevant data about a character from Wikipedia."""
        profile_data = {
            'name': character_name,
            'background': {},
            'traits': {},
            'relationships': {},
            'source': 'wikipedia'
        }
        
        return self.enrich_profile(profile_data, character_name)
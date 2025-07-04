import re
from typing import List, Dict, Any
from openai import OpenAI
from app.core.config import settings
from app.services.founder_search_service import FounderSearchService
from app.services.google_search_service import GoogleSearchService

class EnhancedFounderSearch:
    def __init__(self):
        if not settings.openai_api_key:
            raise ValueError("OpenAI API key not configured")
        
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.founder_search_service = FounderSearchService()
        self.google_search_service = GoogleSearchService()
    
    async def extract_and_search_founders(self, deck_content: str, project_name: str) -> List[Dict[str, Any]]:
        """
        Extract founder names from deck content and search for their information
        """
        try:
            # Extract founder names using OpenAI
            founder_names = await self._extract_founder_names(deck_content, project_name)
            
            # Search for each founder using Google
            founders_info = []
            for name in founder_names:
                founder_info = await self._search_founder_info(name, project_name)
                if founder_info:
                    founders_info.append(founder_info)
            
            return founders_info
            
        except Exception as e:
            return [{
                "name": "Error in search",
                "linkedin": "",
                "github": "",
                "bio": f"Error: {str(e)}"
            }]
    
    async def _extract_founder_names(self, deck_content: str, project_name: str) -> List[str]:
        """
        Extract founder names from deck content using OpenAI
        """
        try:
            prompt = f"""
            Extract ONLY real person names from the team section of this project deck.
            
            PROJECT: {project_name}
            CONTENT: {deck_content[:3000]}...
            
            Look for names in sections like:
            - Team
            - Founders
            - Leadership
            - About Us
            - Management
            
            IMPORTANT RULES:
            - Only extract actual person names (e.g., "John Smith", "Maria Garcia")
            - Do NOT include job titles, descriptions, or long phrases
            - Do NOT include text that is not a person's name
            - If no clear names found, return empty list []
            - Names should be 2-4 words maximum
            - Names should not contain special characters or line breaks
            
            Return ONLY a JSON array of names:
            ["John Smith", "Maria Garcia"]
            
            If no names found, return: []
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert at extracting real person names from business documents. Only return actual names, not descriptions or roles."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )
            
            names_text = response.choices[0].message.content or "[]"
            
            # Parse JSON response
            import json
            try:
                names = json.loads(names_text)
                if isinstance(names, list):
                    # Filter out invalid names
                    valid_names = []
                    for name in names:
                        if (isinstance(name, str) and 
                            len(name.strip()) > 2 and 
                            len(name.strip()) < 50 and
                            not any(char in name for char in ['\n', '\r', '\t', '•', '-', '|']) and
                            name.strip() and
                            len(name.split()) <= 4):  # Max 4 words
                            valid_names.append(name.strip())
                    return valid_names[:5]  # Limit to 5 founders
                return []
            except:
                # Fallback: extract names using regex
                return self._extract_names_regex(deck_content)
                
        except Exception as e:
            return self._extract_names_regex(deck_content)
    
    def _extract_names_regex(self, content: str) -> List[str]:
        """
        Fallback method to extract names using regex patterns
        """
        # Common patterns for finding names in business documents
        patterns = [
            r'(?:CEO|CTO|CMO|CFO|Founder|Co-founder|Director|Head of|VP|President|CEO|CTO)\s*[:\-]?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})',
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})\s*(?:CEO|CTO|CMO|CFO|Founder|Co-founder|Director|Head of|VP|President)',
            r'(?:by|from)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})',
        ]
        
        names = set()
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    names.update(match)
                else:
                    names.add(match)
        
        # Filter names
        valid_names = []
        for name in names:
            if (len(name.strip()) > 2 and 
                len(name.strip()) < 50 and
                len(name.split()) <= 4):
                valid_names.append(name.strip())
        
        return valid_names[:5]  # Limit to 5 names
    
    async def _search_founder_info(self, name: str, company: str) -> Dict[str, Any]:
        """
        Search for founder information using Google and other services
        """
        try:
            # Try Google search first
            google_info = await self.google_search_service.search_person(name, company)
            
            # Try GitHub search as backup
            github_info = await self.founder_search_service._get_github_profile(name)
            
            # Combine information
            return {
                "name": name,
                "linkedin": google_info.get("linkedin", ""),
                "twitter": google_info.get("twitter", ""),
                "github": google_info.get("github", "") or (github_info.get("login", "") if github_info else ""),
                "bio": google_info.get("bio", "No information found"),
                "company": google_info.get("company", company),
                "search_successful": google_info.get("search_successful", False)
            }
            
        except Exception as e:
            return {
                "name": name,
                "linkedin": "",
                "twitter": "",
                "github": "",
                "bio": f"Error in search: {str(e)}",
                "company": company,
                "search_successful": False
            } 
import requests
from bs4 import BeautifulSoup
import re
from typing import List, Optional, Dict, Any
from app.models.schemas import FounderInfo
import json

class FounderSearchService:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    async def search_founders(self, project_name: str, company_name: Optional[str] = None) -> List[FounderInfo]:
        """
        Search for founders of a project/company
        """
        founders = []
        
        # Search strategies
        search_terms = [project_name]
        if company_name and company_name != project_name:
            search_terms.append(company_name)
        
        for term in search_terms:
            # Search LinkedIn
            linkedin_founders = await self._search_linkedin(term)
            founders.extend(linkedin_founders)
            
            # Search Twitter/X
            twitter_founders = await self._search_twitter(term)
            founders.extend(twitter_founders)
            
            # Search GitHub
            github_founders = await self._search_github(term)
            founders.extend(github_founders)
        
        # Remove duplicates and return
        return self._deduplicate_founders(founders)
    
    async def _search_linkedin(self, company_name: str) -> List[FounderInfo]:
        """
        Search LinkedIn for company founders
        """
        try:
            # This is a simplified approach - in production you'd use LinkedIn API
            search_url = f"https://www.linkedin.com/search/results/companies/?keywords={company_name}"
            
            # Note: LinkedIn has anti-bot measures, so this is a placeholder
            # In production, you'd need to use LinkedIn's API or a service like Apollo
            
            return []
            
        except Exception as e:
            print(f"Error searching LinkedIn: {e}")
            return []
    
    async def _search_twitter(self, company_name: str) -> List[FounderInfo]:
        """
        Search Twitter/X for company founders
        """
        try:
            # This is a simplified approach - in production you'd use Twitter API
            search_url = f"https://twitter.com/search?q={company_name}%20founder&src=typed_query"
            
            # Note: Twitter has API restrictions, so this is a placeholder
            # In production, you'd need to use Twitter's API
            
            return []
            
        except Exception as e:
            print(f"Error searching Twitter: {e}")
            return []
    
    async def _search_github(self, project_name: str) -> List[FounderInfo]:
        """
        Search GitHub for project contributors/founders
        """
        try:
            # Search GitHub repositories
            search_url = f"https://api.github.com/search/repositories?q={project_name}"
            
            response = self.session.get(search_url)
            if response.status_code == 200:
                data = response.json()
                founders = []
                
                for repo in data.get('items', [])[:5]:  # Top 5 results
                    # Get repository contributors
                    contributors_url = repo['contributors_url']
                    contributors_response = self.session.get(contributors_url)
                    
                    if contributors_response.status_code == 200:
                        contributors = contributors_response.json()
                        
                        for contributor in contributors[:3]:  # Top 3 contributors
                            founder = FounderInfo(
                                name=contributor.get('login', ''),
                                github_username=contributor.get('login', ''),
                                bio=contributor.get('bio', ''),
                                company=repo.get('name', ''),
                                location=contributor.get('location', '')
                            )
                            founders.append(founder)
                
                return founders
            
            return []
            
        except Exception as e:
            print(f"Error searching GitHub: {e}")
            return []
    
    async def get_founder_details(self, founder_name: str) -> Optional[FounderInfo]:
        """
        Get detailed information about a specific founder
        """
        try:
            # Search for the founder's profiles
            founder = FounderInfo(name=founder_name)
            
            # Try to find GitHub profile
            github_profile = await self._get_github_profile(founder_name)
            if github_profile:
                founder.github_username = github_profile.get('login', '')
                founder.bio = github_profile.get('bio', '')
                founder.location = github_profile.get('location', '')
                founder.company = github_profile.get('company', '')
            
            # Try to find LinkedIn profile
            linkedin_profile = await self._get_linkedin_profile(founder_name)
            if linkedin_profile:
                founder.linkedin_url = linkedin_profile.get('url', '')
            
            # Try to find Twitter profile
            twitter_profile = await self._get_twitter_profile(founder_name)
            if twitter_profile:
                founder.twitter_url = twitter_profile.get('url', '')
            
            return founder
            
        except Exception as e:
            print(f"Error getting founder details: {e}")
            return None
    
    async def _get_github_profile(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Get GitHub profile information
        """
        try:
            url = f"https://api.github.com/users/{username}"
            response = self.session.get(url)
            
            if response.status_code == 200:
                return response.json()
            return None
            
        except Exception:
            return None
    
    async def _get_linkedin_profile(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get LinkedIn profile information (placeholder)
        """
        # This would require LinkedIn API access
        return None
    
    async def _get_twitter_profile(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Get Twitter profile information (placeholder)
        """
        # This would require Twitter API access
        return None
    
    def _deduplicate_founders(self, founders: List[FounderInfo]) -> List[FounderInfo]:
        """
        Remove duplicate founders based on name and GitHub username
        """
        seen = set()
        unique_founders = []
        
        for founder in founders:
            key = (founder.name.lower(), founder.github_username or '')
            if key not in seen:
                seen.add(key)
                unique_founders.append(founder)
        
        return unique_founders 
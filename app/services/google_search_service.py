import requests
from bs4 import BeautifulSoup
import re
from typing import Dict, Any, List
import time

class GoogleSearchService:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    async def search_person(self, name: str, company: str = "") -> Dict[str, Any]:
        """
        Search for a person on Google and extract relevant information
        """
        try:
            # Create search query
            search_query = f'"{name}"'
            if company:
                search_query += f' "{company}"'
            
            # Search on Google
            search_url = f"https://www.google.com/search?q={search_query.replace(' ', '+')}"
            
            response = self.session.get(search_url)
            if response.status_code != 200:
                return self._empty_result(name)
            
            # Parse the response
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract information
            info = self._extract_person_info(soup, name, company)
            
            return info
            
        except Exception as e:
            return self._empty_result(name, f"Error: {str(e)}")
    
    def _extract_person_info(self, soup: BeautifulSoup, name: str, company: str) -> Dict[str, Any]:
        """
        Extract person information from Google search results
        """
        try:
            # Look for LinkedIn profile
            linkedin_url = self._find_linkedin_url(soup)
            
            # Look for other social profiles
            twitter_url = self._find_twitter_url(soup)
            github_url = self._find_github_url(soup)
            
            # Extract bio from search snippets
            bio = self._extract_bio_from_snippets(soup)
            
            # Extract company information
            company_info = self._extract_company_info(soup, company)
            
            return {
                "name": name,
                "linkedin": linkedin_url,
                "twitter": twitter_url,
                "github": github_url,
                "bio": bio,
                "company": company_info,
                "search_successful": True
            }
            
        except Exception as e:
            return self._empty_result(name, f"Error extracting info: {str(e)}")
    
    def _find_linkedin_url(self, soup: BeautifulSoup) -> str:
        """
        Find LinkedIn profile URL in search results
        """
        try:
            # Look for LinkedIn URLs in links
            links = soup.find_all('a', href=True)
            for link in links:
                href = link.get('href', '')
                if 'linkedin.com/in/' in href:
                    # Extract the actual URL from Google's redirect
                    if href.startswith('/url?q='):
                        actual_url = href.split('/url?q=')[1].split('&')[0]
                        return actual_url
                    return href
            return ""
        except:
            return ""
    
    def _find_twitter_url(self, soup: BeautifulSoup) -> str:
        """
        Find Twitter profile URL in search results
        """
        try:
            links = soup.find_all('a', href=True)
            for link in links:
                href = link.get('href', '')
                if 'twitter.com/' in href or 'x.com/' in href:
                    if href.startswith('/url?q='):
                        actual_url = href.split('/url?q=')[1].split('&')[0]
                        return actual_url
                    return href
            return ""
        except:
            return ""
    
    def _find_github_url(self, soup: BeautifulSoup) -> str:
        """
        Find GitHub profile URL in search results
        """
        try:
            links = soup.find_all('a', href=True)
            for link in links:
                href = link.get('href', '')
                if 'github.com/' in href:
                    if href.startswith('/url?q='):
                        actual_url = href.split('/url?q=')[1].split('&')[0]
                        return actual_url
                    return href
            return ""
        except:
            return ""
    
    def _extract_bio_from_snippets(self, soup: BeautifulSoup) -> str:
        """
        Extract bio information from search result snippets
        """
        try:
            # Look for snippet text
            snippets = soup.find_all('div', class_='VwiC3b')
            if not snippets:
                snippets = soup.find_all('span', class_='aCOpRe')
            
            bio_parts = []
            for snippet in snippets[:3]:  # Take first 3 snippets
                text = snippet.get_text().strip()
                if text and len(text) > 20:
                    bio_parts.append(text)
            
            if bio_parts:
                return " ".join(bio_parts)[:300] + "..."  # Limit length
            
            return "No bio information found"
            
        except:
            return "No bio information found"
    
    def _extract_company_info(self, soup: BeautifulSoup, company: str) -> str:
        """
        Extract company information from search results
        """
        try:
            if not company:
                return ""
            
            # Look for company mentions in snippets
            snippets = soup.find_all('div', class_='VwiC3b')
            if not snippets:
                snippets = soup.find_all('span', class_='aCOpRe')
            
            for snippet in snippets:
                text = snippet.get_text()
                if company.lower() in text.lower():
                    return company
            
            return company
            
        except:
            return company if company else ""
    
    def _empty_result(self, name: str, error: str = "") -> Dict[str, Any]:
        """
        Return empty result structure
        """
        return {
            "name": name,
            "linkedin": "",
            "twitter": "",
            "github": "",
            "bio": error if error else "No information found",
            "company": "",
            "search_successful": False
        } 
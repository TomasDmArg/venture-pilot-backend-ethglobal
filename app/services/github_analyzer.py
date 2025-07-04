import re
from typing import List, Dict, Any
from openai import OpenAI
from app.core.config import settings

class GitHubAnalyzer:
    def __init__(self):
        if not settings.openai_api_key:
            raise ValueError("OpenAI API key not configured")
        
        self.client = OpenAI(api_key=settings.openai_api_key)
    
    async def analyze_github_repos(self, deck_content: str, founders: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Analyze GitHub repositories mentioned in the deck or associated with founders
        """
        try:
            # Extract GitHub URLs from deck content
            github_urls = self._extract_github_urls(deck_content)
            
            # Get GitHub usernames from founders
            founder_usernames = [f.get("github", "") for f in founders if f.get("github")]
            
            # Analyze repositories
            repos_analysis = []
            
            # Analyze URLs found in deck
            for url in github_urls:
                repo_info = await self._analyze_repository(url)
                if repo_info:
                    repos_analysis.append(repo_info)
            
            # Analyze founder repositories
            for username in founder_usernames:
                if username:
                    user_repos = await self._get_user_repos(username)
                    repos_analysis.extend(user_repos)
            
            return repos_analysis[:5]  # Limit to 5 repos
            
        except Exception as e:
            return [{
                "repo": "Error en análisis",
                "activity": "Error",
                "main_lang": "N/A",
                "description": f"Error: {str(e)}"
            }]
    
    def _extract_github_urls(self, content: str) -> List[str]:
        """
        Extract GitHub URLs from content
        """
        # GitHub URL patterns
        patterns = [
            r'https://github\.com/[a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+',
            r'github\.com/[a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+',
        ]
        
        urls = []
        for pattern in patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                if not match.startswith('http'):
                    match = 'https://' + match
                urls.append(match)
        
        return list(set(urls))  # Remove duplicates
    
    async def _analyze_repository(self, repo_url: str) -> Dict[str, Any]:
        """
        Analyze a specific GitHub repository
        """
        try:
            # Extract owner and repo name from URL
            parts = repo_url.replace('https://github.com/', '').split('/')
            if len(parts) != 2:
                return {
                    "repo": repo_url,
                    "name": "Error",
                    "description": "URL inválida",
                    "main_lang": "N/A",
                    "stars": 0,
                    "forks": 0,
                    "activity": "Error",
                    "last_updated": "",
                    "size": 0
                }
            
            owner, repo_name = parts
            
            # Get repo info from GitHub API
            import requests
            api_url = f"https://api.github.com/repos/{owner}/{repo_name}"
            
            response = requests.get(api_url)
            if response.status_code != 200:
                return {
                    "repo": repo_url,
                    "name": "Error",
                    "description": "Repositorio no encontrado",
                    "main_lang": "N/A",
                    "stars": 0,
                    "forks": 0,
                    "activity": "Error",
                    "last_updated": "",
                    "size": 0
                }
            
            repo_data = response.json()
            
            return {
                "repo": repo_url,
                "name": repo_data.get("name", ""),
                "description": repo_data.get("description", ""),
                "main_lang": repo_data.get("language", "N/A"),
                "stars": repo_data.get("stargazers_count", 0),
                "forks": repo_data.get("forks_count", 0),
                "activity": self._assess_activity(repo_data),
                "last_updated": repo_data.get("updated_at", ""),
                "size": repo_data.get("size", 0)
            }
            
        except Exception as e:
            return {
                "repo": repo_url,
                "name": "Error",
                "description": f"Error analyzing repo: {str(e)}",
                "main_lang": "N/A",
                "stars": 0,
                "forks": 0,
                "activity": "Error",
                "last_updated": "",
                "size": 0
            }
    
    async def _get_user_repos(self, username: str) -> List[Dict[str, Any]]:
        """
        Get top repositories for a GitHub user
        """
        try:
            import requests
            api_url = f"https://api.github.com/users/{username}/repos"
            
            response = requests.get(api_url)
            if response.status_code != 200:
                return []
            
            repos_data = response.json()
            
            # Sort by stars and get top 3
            sorted_repos = sorted(repos_data, key=lambda x: x.get("stargazers_count", 0), reverse=True)
            
            user_repos = []
            for repo in sorted_repos[:3]:
                user_repos.append({
                    "repo": repo.get("html_url", ""),
                    "name": repo.get("name", ""),
                    "description": repo.get("description", ""),
                    "main_lang": repo.get("language", "N/A"),
                    "stars": repo.get("stargazers_count", 0),
                    "forks": repo.get("forks_count", 0),
                    "activity": self._assess_activity(repo),
                    "last_updated": repo.get("updated_at", ""),
                    "size": repo.get("size", 0)
                })
            
            return user_repos
            
        except Exception as e:
            return []
    
    def _assess_activity(self, repo_data: Dict[str, Any]) -> str:
        """
        Assess repository activity level
        """
        try:
            # Get last update date
            updated_at = repo_data.get("updated_at", "")
            if not updated_at:
                return "Desconocido"
            
            from datetime import datetime
            last_update = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
            now = datetime.now(last_update.tzinfo)
            
            days_since_update = (now - last_update).days
            
            if days_since_update <= 7:
                return "Muy Alta"
            elif days_since_update <= 30:
                return "Alta"
            elif days_since_update <= 90:
                return "Media"
            else:
                return "Baja"
                
        except Exception:
            return "Desconocido" 
import re
import logging
from typing import List, Dict, Any, Optional
from openai import OpenAI
from app.core.config import settings
from app.services.founder_search_service import FounderSearchService
from app.services.google_search_service import GoogleSearchService
from app.services.gitroll_service import GitRollService

# Setup logging
logger = logging.getLogger(__name__)

class EnhancedFounderSearch:
    def __init__(self):
        if not settings.openai_api_key:
            raise ValueError("OpenAI API key not configured")
        
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.founder_search_service = FounderSearchService()
        self.google_search_service = GoogleSearchService()
        self.gitroll_service = GitRollService()
    
    async def extract_and_search_founders(self, deck_content: str, project_name: str) -> List[Dict[str, Any]]:
        """
        Extract founder names from deck content and search for their information
        """
        try:
            logger.info(f"Starting founder extraction for project: {project_name}")
            
            # Extract founder names and bios using OpenAI
            logger.info("Extracting founders with bios from deck content...")
            founders_data = await self._extract_founders_with_bios(deck_content, project_name)
            logger.info(f"Found {len(founders_data)} founders in deck")
            
            # Search for each founder using multiple sources
            founders_info = []
            for i, founder_data in enumerate(founders_data):
                logger.info(f"Processing founder {i+1}/{len(founders_data)}: {founder_data['name']}")
                founder_info = await self._search_founder_info_comprehensive(
                    founder_data["name"], 
                    project_name, 
                    founder_data.get("bio", ""),
                    founder_data.get("role", "")
                )
                if founder_info:
                    founders_info.append(founder_info)
                    logger.info(f"Completed analysis for {founder_data['name']} - Score: {founder_info.get('score', 0)}")
            
            logger.info(f"Completed founder analysis for {project_name}. Total founders processed: {len(founders_info)}")
            return founders_info
            
        except Exception as e:
            logger.error(f"Error in founder extraction: {str(e)}")
            return [{
                "name": "Error in search",
                "linkedin": "",
                "github": "",
                "bio": f"Error: {str(e)}",
                "score": 0,
                "contribution": "Error occurred during search"
            }]
    
    async def _extract_founders_with_bios(self, deck_content: str, project_name: str) -> List[Dict[str, Any]]:
        """
        Extract founder names, roles, and bios from deck content using OpenAI
        """
        try:
            prompt = f"""
            Extract founder information from the team section of this project deck.
            
            PROJECT: {project_name}
            CONTENT: {deck_content[:4000]}...
            
            Look for information in sections like:
            - Team
            - Founders
            - Leadership
            - About Us
            - Management
            - Our Team
            
            IMPORTANT RULES:
            - Extract actual person names with their roles and bios
            - Include any background information, experience, or bio text
            - Focus on founders, co-founders, CEOs, CTOs, and key leadership
            - If no clear team info found, return empty list []
            - All output must be in English
            
            Return ONLY a JSON array of founder objects:
            [
                {{
                    "name": "John Smith",
                    "role": "CEO & Co-founder",
                    "bio": "Former Google engineer with 10 years experience in AI"
                }},
                {{
                    "name": "Maria Garcia",
                    "role": "CTO & Co-founder", 
                    "bio": "PhD in Computer Science from Stanford, expert in machine learning"
                }}
            ]
            
            If no founders found, return: []
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert at extracting founder information from business documents. Extract names, roles, and bios. Always respond in English."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )
            
            founders_text = response.choices[0].message.content or "[]"
            
            # Parse JSON response
            import json
            try:
                founders = json.loads(founders_text)
                if isinstance(founders, list):
                    # Filter out invalid entries
                    valid_founders = []
                    for founder in founders:
                        if (isinstance(founder, dict) and 
                            founder.get("name") and
                            len(founder["name"].strip()) > 2 and 
                            len(founder["name"].strip()) < 100):
                            valid_founders.append({
                                "name": founder["name"].strip(),
                                "role": founder.get("role", "").strip(),
                                "bio": founder.get("bio", "").strip()
                            })
                    return valid_founders[:10]  # Limit to 10 founders
                return []
            except:
                # Fallback: extract names using regex
                return self._extract_names_regex(deck_content)
                
        except Exception as e:
            return self._extract_names_regex(deck_content)
    
    def _extract_names_regex(self, content: str) -> List[Dict[str, Any]]:
        """
        Fallback method to extract names using regex patterns
        """
        # Common patterns for finding names in business documents
        patterns = [
            r'(?:CEO|CTO|CMO|CFO|Founder|Co-founder|Director|Head of|VP|President)\s*[:\-]?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})',
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})\s*(?:CEO|CTO|CMO|CFO|Founder|Co-founder|Director|Head of|VP|President)',
        ]
        
        names = set()
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    names.update(match)
                else:
                    names.add(match)
        
        # Convert to founder objects
        founders = []
        for name in names:
            if (len(name.strip()) > 2 and 
                len(name.strip()) < 100 and
                len(name.split()) <= 4):
                founders.append({
                    "name": name.strip(),
                    "role": "",
                    "bio": ""
                })
        
        return founders[:5]  # Limit to 5 names
    
    async def _search_founder_info_comprehensive(self, name: str, company: str, deck_bio: str = "", role: str = "") -> Dict[str, Any]:
        """
        Search for founder information using multiple sources and score them
        """
        try:
            logger.info(f"Starting comprehensive search for {name}")
            
            # Try Google search first
            logger.info(f"Searching Google for {name}...")
            google_info = await self.google_search_service.search_person(name, company)
            logger.info(f"Google search completed for {name}")
            
            # Try GitHub search
            logger.info(f"Searching GitHub for {name}...")
            github_info = await self.founder_search_service._get_github_profile(name)
            if github_info:
                logger.info(f"Found GitHub profile for {name}: {github_info.get('login', 'N/A')}")
            else:
                logger.info(f"No GitHub profile found for {name}")
            
            # Try GitRoll if we have GitHub username
            gitroll_info = None
            if github_info and github_info.get("login"):
                logger.info(f"Initiating GitRoll scan for {github_info['login']}...")
                gitroll_result = await self.gitroll_service.initiate_scan(github_info["login"])
                if gitroll_result.success and gitroll_result.scan_id:
                    logger.info(f"GitRoll scan initiated for {github_info['login']}, waiting for completion...")
                    # Wait for scan completion
                    gitroll_info = await self.gitroll_service.wait_for_scan_completion(gitroll_result.scan_id)
                    # Add user_id to gitroll_info
                    if gitroll_info:
                        gitroll_info["user_id"] = gitroll_result.user_id
                        logger.info(f"GitRoll scan completed for {github_info['login']} - Score: {gitroll_info.get('score', 'N/A')}")
                else:
                    logger.warning(f"GitRoll scan failed for {github_info['login']}")
            else:
                logger.info(f"Skipping GitRoll scan for {name} - no GitHub username found")
            
            # Score the founder
            logger.info(f"Scoring founder {name}...")
            founder_score = await self._score_founder(name, deck_bio, role, google_info, github_info, gitroll_info)
            logger.info(f"Scoring completed for {name} - Overall Score: {founder_score['score']}")
            
            # Combine information
            return {
                "name": name,
                "role": role,
                "deck_bio": deck_bio,
                "linkedin": google_info.get("linkedin", ""),
                "twitter": google_info.get("twitter", ""),
                "github": google_info.get("github", "") or (github_info.get("login", "") if github_info else ""),
                "bio": google_info.get("bio", deck_bio) if google_info.get("bio") else deck_bio,
                "company": google_info.get("company", company),
                "score": founder_score["score"],
                "contribution": founder_score["contribution"],
                "technical_score": founder_score["technical_score"],
                "business_score": founder_score["business_score"],
                "gitroll_user_id": gitroll_info.get("user_id") if gitroll_info and gitroll_info.get("success") else None,
                "gitroll_score": gitroll_info.get("score") if gitroll_info and gitroll_info.get("success") else None,
                "search_successful": google_info.get("search_successful", False)
            }
            
        except Exception as e:
            logger.error(f"Error in comprehensive search for {name}: {str(e)}")
            return {
                "name": name,
                "role": role,
                "deck_bio": deck_bio,
                "linkedin": "",
                "twitter": "",
                "github": "",
                "bio": deck_bio or f"Error in search: {str(e)}",
                "company": company,
                "score": 0,
                "contribution": "Error occurred during search",
                "technical_score": 0,
                "business_score": 0,
                "gitroll_user_id": None,
                "gitroll_score": None,
                "search_successful": False
            }
    
    async def _score_founder(self, name: str, deck_bio: str, role: str, google_info: Dict[str, Any], github_info: Optional[Dict[str, Any]], gitroll_info: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Score a founder based on their background and contributions
        """
        try:
            # Combine all available information
            combined_info = f"""
            Name: {name}
            Role: {role}
            Deck Bio: {deck_bio}
            Google Bio: {google_info.get('bio', '')}
            GitHub Bio: {github_info.get('bio', '') if github_info else ''}
            GitRoll Score: {gitroll_info.get('score', 'N/A') if gitroll_info else 'N/A'}
            """
            
            prompt = f"""
            Analyze this founder's profile and provide a comprehensive score and assessment.
            
            FOUNDER INFO:
            {combined_info}
            
            Please provide your analysis in the following JSON format:
            {{
                "score": 8.5,
                "technical_score": 7.0,
                "business_score": 9.0,
                "contribution": "Strong technical background with proven business acumen. Former Google engineer with 10+ years experience in AI and machine learning. Excellent track record of building and scaling products.",
                "strengths": ["Technical expertise", "Industry experience", "Leadership skills"],
                "areas_for_improvement": ["Could benefit from more startup experience"]
            }}
            
            SCORING CRITERIA:
            - Overall Score (1-10): Overall assessment of founder's potential
            - Technical Score (1-10): Technical skills, engineering background, relevant expertise
            - Business Score (1-10): Business acumen, leadership, market understanding
            - Contribution: Detailed explanation of what they bring to the project
            - Strengths: Key positive attributes
            - Areas for Improvement: Potential weaknesses or gaps
            
            Consider:
            - Technical background (engineering, computer science, etc.)
            - Business experience (management, entrepreneurship, etc.)
            - Industry relevance to the project
            - Track record and achievements
            - Leadership and communication skills
            
            All output must be in English.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert startup analyst specializing in founder evaluation. Provide objective, detailed assessments in English."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )
            
            analysis_text = response.choices[0].message.content or "{}"
            
            # Parse JSON response
            import json
            try:
                analysis = json.loads(analysis_text)
                return {
                    "score": analysis.get("score", 5.0),
                    "technical_score": analysis.get("technical_score", 5.0),
                    "business_score": analysis.get("business_score", 5.0),
                    "contribution": analysis.get("contribution", "Limited information available"),
                    "strengths": analysis.get("strengths", []),
                    "areas_for_improvement": analysis.get("areas_for_improvement", [])
                }
            except:
                # Fallback scoring
                return {
                    "score": 5.0,
                    "technical_score": 5.0,
                    "business_score": 5.0,
                    "contribution": "Limited information available for comprehensive assessment",
                    "strengths": [],
                    "areas_for_improvement": []
                }
                
        except Exception as e:
            return {
                "score": 5.0,
                "technical_score": 5.0,
                "business_score": 5.0,
                "contribution": f"Error in scoring: {str(e)}",
                "strengths": [],
                "areas_for_improvement": []
            } 
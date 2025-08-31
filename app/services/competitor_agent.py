import requests
import logging
from typing import List, Dict, Any
from openai import OpenAI
from app.core.config import settings
from bs4 import BeautifulSoup
import re

# Setup logging
logger = logging.getLogger(__name__)

class CompetitorAgent:
    def __init__(self):
        if not settings.openai_api_key:
            raise ValueError("OpenAI API key not configured")
        
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    async def analyze_competitors(self, project_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze competitors for a given project
        """
        try:
            logger.info(f"Starting competitor analysis for: {project_info.get('project_name', 'Unknown')}")
            
            # Extract key search terms
            search_terms = self._generate_search_terms(project_info)
            logger.info(f"Generated search terms: {search_terms}")
            
            # Search for competitors
            competitors = []
            for term in search_terms[:3]:  # Limit to top 3 search terms
                logger.info(f"Searching for competitors with term: {term}")
                term_competitors = await self._search_competitors(term)
                competitors.extend(term_competitors)
            
            # Remove duplicates and analyze
            unique_competitors = self._deduplicate_competitors(competitors)
            logger.info(f"Found {len(unique_competitors)} unique competitors")
            
            # Analyze competitive landscape
            competitive_analysis = await self._analyze_competitive_landscape(project_info, unique_competitors)
            
            return {
                "competitors": unique_competitors,
                "competitive_analysis": competitive_analysis,
                "market_saturation": self._calculate_market_saturation(len(unique_competitors)),
                "competitive_advantage": competitive_analysis.get("competitive_advantage", ""),
                "threat_level": competitive_analysis.get("threat_level", "medium")
            }
            
        except Exception as e:
            logger.error(f"Error in competitor analysis: {str(e)}")
            return {
                "competitors": [],
                "competitive_analysis": {"error": str(e)},
                "market_saturation": "unknown",
                "competitive_advantage": "Analysis failed",
                "threat_level": "unknown"
            }
    
    def _generate_search_terms(self, project_info: Dict[str, Any]) -> List[str]:
        """
        Generate search terms for competitor analysis
        """
        project_name = project_info.get('project_name', '')
        description = project_info.get('description', '')
        target_market = project_info.get('target_market', '')
        
        # Extract key terms
        terms = []
        
        # Add project name variations
        if project_name:
            terms.append(f'"{project_name}" competitors')
            terms.append(f'"{project_name}" alternatives')
        
        # Add description-based terms
        if description:
            # Extract key phrases from description
            key_phrases = self._extract_key_phrases(description)
            for phrase in key_phrases[:3]:
                terms.append(f'"{phrase}" companies')
        
        # Add market-based terms
        if target_market:
            terms.append(f'"{target_market}" solutions')
            terms.append(f'"{target_market}" platforms')
        
        return terms
    
    def _extract_key_phrases(self, text: str) -> List[str]:
        """
        Extract key phrases from text for search terms
        """
        # Simple extraction - in production you might use NLP
        phrases = []
        words = text.lower().split()
        
        # Look for 2-3 word phrases
        for i in range(len(words) - 1):
            phrase = f"{words[i]} {words[i+1]}"
            if len(phrase) > 5 and not any(word in phrase for word in ['the', 'and', 'or', 'for', 'with', 'in', 'on', 'at', 'to', 'of', 'a', 'an']):
                phrases.append(phrase)
        
        return phrases[:5]  # Return top 5 phrases
    
    async def _search_competitors(self, search_term: str) -> List[Dict[str, Any]]:
        """
        Search for competitors using Google
        """
        try:
            # This is a simplified approach - in production you'd use a proper search API
            search_url = f"https://www.google.com/search?q={search_term}"
            
            # Note: This is a placeholder. In production, you'd use:
            # - Google Custom Search API
            # - SerpAPI
            # - ScrapingBee
            # - Or other search APIs
            
            # For now, return mock data
            mock_competitors = [
                {
                    "name": f"Competitor A - {search_term}",
                    "description": f"Leading company in {search_term} space",
                    "website": "https://competitor-a.com",
                    "funding": "$50M Series B",
                    "founded": "2020",
                    "employees": "100-250",
                    "relevance_score": 8.5
                },
                {
                    "name": f"Competitor B - {search_term}",
                    "description": f"Emerging player in {search_term} market",
                    "website": "https://competitor-b.com",
                    "funding": "$15M Series A",
                    "founded": "2021",
                    "employees": "25-50",
                    "relevance_score": 7.2
                }
            ]
            
            return mock_competitors
            
        except Exception as e:
            logger.error(f"Error searching competitors for {search_term}: {str(e)}")
            return []
    
    def _deduplicate_competitors(self, competitors: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Remove duplicate competitors based on name similarity
        """
        seen = set()
        unique_competitors = []
        
        for competitor in competitors:
            name_key = competitor.get('name', '').lower().strip()
            if name_key and name_key not in seen:
                seen.add(name_key)
                unique_competitors.append(competitor)
        
        return unique_competitors
    
    async def _analyze_competitive_landscape(self, project_info: Dict[str, Any], competitors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze the competitive landscape using OpenAI
        """
        try:
            logger.info("Analyzing competitive landscape with OpenAI...")
            
            prompt = f"""
            Analyze the competitive landscape for this project and provide insights.
            
            PROJECT INFO:
            - Name: {project_info.get('project_name', 'N/A')}
            - Description: {project_info.get('description', 'N/A')}
            - Target Market: {project_info.get('target_market', 'N/A')}
            - Solution: {project_info.get('solution', 'N/A')}
            
            COMPETITORS FOUND ({len(competitors)}):
            {self._format_competitors_for_analysis(competitors)}
            
            Please provide your analysis in this EXACT JSON format (no additional text before or after):
            {{
                "market_saturation": "high",
                "competitive_advantage": "Clear explanation of what makes this project unique",
                "threat_level": "medium",
                "key_differentiators": [
                    "Differentiator 1",
                    "Differentiator 2"
                ],
                "market_gaps": [
                    "Gap 1 that this project could fill",
                    "Gap 2 that this project could fill"
                ],
                "recommendations": [
                    "Recommendation 1 for competitive positioning",
                    "Recommendation 2 for competitive positioning"
                ]
            }}
            
            Be objective and specific. Consider market saturation, competitive advantages, and potential threats.
            IMPORTANT: Return ONLY the JSON object, no additional text or explanations.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-5-nano-2025-08-07",
                messages=[
                    {"role": "system", "content": "You are an expert competitive analyst specializing in startup evaluation. Provide clear, objective competitive analysis. Always respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=1
            )
            
            analysis_text = response.choices[0].message.content or "{}"
            logger.info(f"Raw competitive analysis response: {analysis_text[:200]}...")
            
            # Parse JSON response with multiple fallback strategies
            analysis = self._parse_competitive_analysis_json(analysis_text)
            logger.info("Competitive landscape analysis completed")
            return analysis
                
        except Exception as e:
            logger.error(f"Error analyzing competitive landscape: {str(e)}")
            return {
                "market_saturation": "unknown",
                "competitive_advantage": f"Error: {str(e)}",
                "threat_level": "unknown",
                "key_differentiators": [],
                "market_gaps": [],
                "recommendations": []
            }
    
    def _format_competitors_for_analysis(self, competitors: List[Dict[str, Any]]) -> str:
        """
        Format competitors for analysis prompt
        """
        formatted = []
        for i, comp in enumerate(competitors[:5], 1):  # Limit to top 5
            formatted.append(f"{i}. {comp.get('name', 'Unknown')} - {comp.get('description', 'No description')}")
        return "\n".join(formatted)
    
    def _parse_competitive_analysis_json(self, analysis_text: str) -> Dict[str, Any]:
        """
        Parse competitive analysis JSON with multiple fallback strategies
        """
        import json
        import re
        
        # Strategy 1: Try to find JSON block with regex
        try:
            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', analysis_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                logger.info(f"Found JSON block: {json_str[:100]}...")
                analysis = json.loads(json_str)
                return self._validate_competitive_analysis(analysis)
        except Exception as e:
            logger.warning(f"Strategy 1 failed: {str(e)}")
        
        # Strategy 2: Try to extract JSON from the entire text
        try:
            # Remove any text before the first {
            start_idx = analysis_text.find('{')
            if start_idx != -1:
                json_str = analysis_text[start_idx:]
                # Find the matching closing brace
                brace_count = 0
                end_idx = -1
                for i, char in enumerate(json_str):
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            end_idx = i + 1
                            break
                
                if end_idx != -1:
                    json_str = json_str[:end_idx]
                    logger.info(f"Extracted JSON: {json_str[:100]}...")
                    analysis = json.loads(json_str)
                    return self._validate_competitive_analysis(analysis)
        except Exception as e:
            logger.warning(f"Strategy 2 failed: {str(e)}")
        
        # Strategy 3: Try to parse the entire text as JSON
        try:
            analysis = json.loads(analysis_text.strip())
            return self._validate_competitive_analysis(analysis)
        except Exception as e:
            logger.warning(f"Strategy 3 failed: {str(e)}")
        
        # Strategy 4: Manual extraction from text
        try:
            analysis = self._extract_competitive_analysis_manually(analysis_text)
            return self._validate_competitive_analysis(analysis)
        except Exception as e:
            logger.warning(f"Strategy 4 failed: {str(e)}")
        
        # Final fallback
        logger.warning("All JSON parsing strategies failed, using fallback")
        return {
            "market_saturation": "medium",
            "competitive_advantage": "Analysis incomplete - manual review recommended",
            "threat_level": "medium",
            "key_differentiators": ["Requires manual analysis"],
            "market_gaps": ["Requires manual analysis"],
            "recommendations": ["Conduct manual competitive analysis"]
        }
    
    def _validate_competitive_analysis(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and clean competitive analysis data
        """
        return {
            "market_saturation": analysis.get("market_saturation", "medium"),
            "competitive_advantage": analysis.get("competitive_advantage", "Analysis incomplete"),
            "threat_level": analysis.get("threat_level", "medium"),
            "key_differentiators": analysis.get("key_differentiators", []) if isinstance(analysis.get("key_differentiators"), list) else [],
            "market_gaps": analysis.get("market_gaps", []) if isinstance(analysis.get("market_gaps"), list) else [],
            "recommendations": analysis.get("recommendations", []) if isinstance(analysis.get("recommendations"), list) else []
        }
    
    def _extract_competitive_analysis_manually(self, text: str) -> Dict[str, Any]:
        """
        Manually extract competitive analysis from text if JSON parsing fails
        """
        analysis = {
            "market_saturation": "medium",
            "competitive_advantage": "Manual extraction required",
            "threat_level": "medium",
            "key_differentiators": [],
            "market_gaps": [],
            "recommendations": []
        }
        
        # Try to extract market saturation
        if "high" in text.lower() and "saturation" in text.lower():
            analysis["market_saturation"] = "high"
        elif "low" in text.lower() and "saturation" in text.lower():
            analysis["market_saturation"] = "low"
        
        # Try to extract threat level
        if "high" in text.lower() and "threat" in text.lower():
            analysis["threat_level"] = "high"
        elif "low" in text.lower() and "threat" in text.lower():
            analysis["threat_level"] = "low"
        
        # Try to extract competitive advantage
        lines = text.split('\n')
        for line in lines:
            if "advantage" in line.lower() or "unique" in line.lower():
                analysis["competitive_advantage"] = line.strip()
                break
        
        return analysis
    
    def _calculate_market_saturation(self, competitor_count: int) -> str:
        """
        Calculate market saturation based on competitor count
        """
        if competitor_count == 0:
            return "low"
        elif competitor_count <= 3:
            return "low"
        elif competitor_count <= 8:
            return "medium"
        else:
            return "high" 
import base64
import json
from openai import OpenAI
from typing import Dict, Any, Optional
from app.core.config import settings
from app.models.schemas import ProjectSummary, FounderInfo, GitRollScan

class SimpleAnalysisService:
    def __init__(self):
        if not settings.openai_api_key:
            raise ValueError("OpenAI API key not configured. Please set OPENAI_API_KEY in your .env file")
        
        self.client = OpenAI(api_key=settings.openai_api_key)
    
    async def analyze_project(self, deck_file: str, project_name: Optional[str] = None) -> ProjectSummary:
        """
        Simple analysis function using OpenAI directly
        """
        try:
            # Decode base64 deck file
            deck_content = self._decode_deck_file(deck_file)
            
            # Create analysis prompt
            prompt = self._create_analysis_prompt(deck_content, project_name)
            
            # Get analysis from OpenAI
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert business analyst specializing in startup evaluation. Provide clear, structured analysis."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )
            
            # Parse the response
            analysis_text = response.choices[0].message.content or ""
            
            # Extract information
            project_info = self._extract_project_info(analysis_text)
            
            # Create project summary
            return ProjectSummary(
                project_name=project_info.get('project_name', 'Unknown Project'),
                description=project_info.get('description', ''),
                problem_statement=project_info.get('problem_statement', ''),
                solution=project_info.get('solution', ''),
                target_market=project_info.get('target_market', ''),
                business_model=project_info.get('business_model', ''),
                team_info=[],  # Simplified for now
                github_repos=[],  # Simplified for now
                gitroll_scans=[]  # Simplified for now
            )
            
        except Exception as e:
            # Return error summary
            return ProjectSummary(
                project_name="Analysis Failed",
                description=f"Error during analysis: {str(e)}",
                problem_statement="",
                solution="",
                target_market="",
                business_model="",
                team_info=[],
                github_repos=[],
                gitroll_scans=[]
            )
    
    async def analyze_project_content(self, deck_content: str, project_name: Optional[str] = None) -> ProjectSummary:
        """
        Analyze project content directly (without base64 encoding)
        """
        try:
            # Create analysis prompt
            prompt = self._create_analysis_prompt(deck_content, project_name)
            
            # Get analysis from OpenAI
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert business analyst specializing in startup evaluation. Provide clear, structured analysis."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )
            
            # Parse the response
            analysis_text = response.choices[0].message.content or ""
            
            # Extract information
            project_info = self._extract_project_info(analysis_text)
            
            # Create project summary
            return ProjectSummary(
                project_name=project_info.get('project_name', 'Unknown Project'),
                description=project_info.get('description', ''),
                problem_statement=project_info.get('problem_statement', ''),
                solution=project_info.get('solution', ''),
                target_market=project_info.get('target_market', ''),
                business_model=project_info.get('business_model', ''),
                team_info=[],  # Simplified for now
                github_repos=[],  # Simplified for now
                gitroll_scans=[]  # Simplified for now
            )
            
        except Exception as e:
            # Return error summary
            return ProjectSummary(
                project_name="Analysis Failed",
                description=f"Error during analysis: {str(e)}",
                problem_statement="",
                solution="",
                target_market="",
                business_model="",
                team_info=[],
                github_repos=[],
                gitroll_scans=[]
            )
    
    def _decode_deck_file(self, deck_file: str) -> str:
        """
        Decode base64 encoded deck file
        """
        try:
            # Remove data URL prefix if present
            if deck_file.startswith('data:'):
                deck_file = deck_file.split(',')[1]
            
            decoded_bytes = base64.b64decode(deck_file)
            return decoded_bytes.decode('utf-8')
        except Exception as e:
            raise ValueError(f"Error decoding deck file: {str(e)}")
    
    def _create_analysis_prompt(self, deck_content: str, project_name: Optional[str]) -> str:
        """
        Create analysis prompt for OpenAI
        """
        return f"""
        Analyze the following project deck and provide a comprehensive analysis in JSON format.
        
        Project Name: {project_name or 'Extract from content'}
        
        Deck Content:
        {deck_content[:3000]}...
        
        Please provide your analysis in the following JSON format:
        {{
            "project_name": "Name of the project",
            "description": "Clear description of what the project does",
            "problem_statement": "What problem is the project trying to solve",
            "solution": "How does the project solve the identified problem",
            "target_market": "Who are the target customers/users",
            "business_model": "How does the project generate revenue",
            "team_info": [
                {{
                    "name": "Team member name",
                    "role": "Role in the project",
                    "background": "Brief background"
                }}
            ],
            "key_insights": [
                "Key insight 1",
                "Key insight 2",
                "Key insight 3"
            ],
            "recommendations": [
                "Recommendation 1",
                "Recommendation 2"
            ]
        }}
        
        Focus on providing actionable insights and clear, business-focused analysis.
        """
    
    def _extract_project_info(self, analysis_text: str) -> Dict[str, Any]:
        """
        Extract project information from OpenAI response
        """
        try:
            # Try to find JSON in the response
            import re
            
            # Look for JSON blocks
            json_match = re.search(r'\{.*\}', analysis_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                return json.loads(json_str)
            
            # Fallback: create basic structure
            return {
                "project_name": "Extracted Project",
                "description": analysis_text[:200] + "...",
                "problem_statement": "Analysis completed",
                "solution": "See full analysis",
                "target_market": "See full analysis",
                "business_model": "See full analysis"
            }
            
        except Exception as e:
            return {
                "project_name": "Analysis Error",
                "description": f"Error parsing analysis: {str(e)}",
                "problem_statement": "",
                "solution": "",
                "target_market": "",
                "business_model": ""
            } 
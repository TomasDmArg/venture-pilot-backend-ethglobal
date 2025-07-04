from openai import OpenAI
import logging
from typing import Dict, Any
from app.core.config import settings

# Setup logging
logger = logging.getLogger(__name__)

class ViabilityAgent:
    def __init__(self):
        if not settings.openai_api_key:
            raise ValueError("OpenAI API key not configured")
        
        self.client = OpenAI(api_key=settings.openai_api_key)
    
    async def assess_viability(self, project_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess project viability from VC perspective
        """
        try:
            logger.info(f"Starting viability assessment for project: {project_info.get('project_name', 'Unknown')}")
            
            # Create assessment prompt
            prompt = self._create_viability_prompt(project_info)
            
            # Get assessment from OpenAI
            logger.info("Generating viability assessment with OpenAI...")
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert VC analyst. Provide clear, objective viability assessments."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )
            
            assessment_text = response.choices[0].message.content or ""
            logger.info("Viability assessment generated successfully")
            
            # Parse the assessment
            result = self._parse_viability_assessment(assessment_text)
            logger.info(f"Viability assessment completed - Score: {result.get('score', 'N/A')}")
            return result
            
        except Exception as e:
            logger.error(f"Error in viability assessment: {str(e)}")
            return {
                "score": 5,
                "explanation": f"Error in evaluation: {str(e)}",
                "risk_factors": ["Technical error"],
                "strengths": []
            }
    
    def _create_viability_prompt(self, project_info: Dict[str, Any]) -> str:
        """
        Create viability assessment prompt
        """
        return f"""
        Assess the viability of this project from a VC (Venture Capital) perspective.
        
        PROJECT INFORMATION:
        - Name: {project_info.get('project_name', 'N/A')}
        - Description: {project_info.get('description', 'N/A')}
        - Problem: {project_info.get('problem_statement', 'N/A')}
        - Solution: {project_info.get('solution', 'N/A')}
        - Target Market: {project_info.get('target_market', 'N/A')}
        - Business Model: {project_info.get('business_model', 'N/A')}
        - Team: {project_info.get('team_info', [])}
        
        EVALUATION CRITERIA (1-10):
        1-2: Very high risk, questionable market, weak team
        3-4: High risk, significant problems
        5-6: Medium risk, limited potential
        7-8: Low risk, good potential
        9-10: Very low risk, excellent potential
        
        Provide your assessment in this JSON format:
        {{
            "score": 8,
            "explanation": "Clear and concise explanation of why this score",
            "risk_factors": [
                "Risk factor 1",
                "Risk factor 2"
            ],
            "strengths": [
                "Strength 1",
                "Strength 2"
            ],
            "recommendation": "Invest / Don't invest / More research needed"
        }}
        
        Be objective and specific. Consider: market size, competition, team, technology, scalability, and business model.
        All output must be in English.
        """
    
    def _parse_viability_assessment(self, assessment_text: str) -> Dict[str, Any]:
        """
        Parse viability assessment from OpenAI response
        """
        try:
            import re
            import json
            
            # Look for JSON in the response
            json_match = re.search(r'\{.*\}', assessment_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                return json.loads(json_str)
            
            # Fallback
            return {
                "score": 5,
                "explanation": assessment_text[:200] + "...",
                "risk_factors": ["Incomplete analysis"],
                "strengths": [],
                "recommendation": "More research needed"
            }
            
        except Exception as e:
            return {
                "score": 5,
                "explanation": f"Error parsing assessment: {str(e)}",
                "risk_factors": ["Technical error"],
                "strengths": [],
                "recommendation": "More research needed"
            } 
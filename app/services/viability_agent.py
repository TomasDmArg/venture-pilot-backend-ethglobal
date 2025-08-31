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
                model="gpt-5-nano-2025-08-07",
                messages=[
                    {"role": "system", "content": "You are an expert VC analyst. Provide clear, objective viability assessments."},
                    {"role": "user", "content": prompt}
                ],
                temperature=1
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
        Create viability assessment prompt with stricter criteria
        """
        return f"""
        Assess the viability of this project from a VC perspective using STRICT evaluation criteria.
        
        PROJECT INFORMATION:
        - Name: {project_info.get('project_name', 'N/A')}
        - Description: {project_info.get('description', 'N/A')}
        - Problem: {project_info.get('problem_statement', 'N/A')}
        - Solution: {project_info.get('solution', 'N/A')}
        - Target Market: {project_info.get('target_market', 'N/A')}
        - Business Model: {project_info.get('business_model', 'N/A')}
        - Team: {project_info.get('team_info', [])}
        
        STRICT EVALUATION CRITERIA (1-10):
        
        SCORING BREAKDOWN:
        - Team Quality (30%): Experience, track record, technical skills, leadership
        - Market Opportunity (25%): Market size, growth potential, customer demand
        - Product/Solution (20%): Innovation, technical feasibility, competitive advantage
        - Business Model (15%): Revenue potential, scalability, unit economics
        - Execution Risk (10%): Implementation challenges, timeline, resources
        
        PENALTY FACTORS (DEDUCT POINTS):
        - Weak team (no relevant experience): -3 points
        - Small market (<$100M TAM): -2 points
        - No clear competitive advantage: -2 points
        - Unproven business model: -2 points
        - High technical risk: -2 points
        - Regulatory/compliance issues: -2 points
        - No traction/customers: -1 point
        - Poor execution plan: -1 point
        
        BONUS FACTORS (ADD POINTS):
        - Strong team with proven track record: +2 points
        - Large, growing market (>$1B TAM): +2 points
        - Clear competitive moat: +2 points
        - Proven business model: +1 point
        - Existing traction/customers: +1 point
        - Strong IP/technology: +1 point
        
        FINAL SCORE INTERPRETATION:
        9-10: Exceptional - Strong investment potential
        7-8: Good - Worth serious consideration
        5-6: Average - Needs significant improvement
        3-4: Poor - High risk, major concerns
        1-2: Very Poor - Avoid investment
        
        Provide your assessment in this JSON format:
        {{
            "score": 6.5,
            "explanation": "Detailed explanation of scoring with specific reasons for deductions/bonuses",
            "team_score": 7.0,
            "market_score": 6.5,
            "product_score": 7.5,
            "business_model_score": 6.0,
            "execution_score": 5.5,
            "risk_factors": [
                "Specific risk factor 1 with impact",
                "Specific risk factor 2 with impact"
            ],
            "strengths": [
                "Specific strength 1",
                "Specific strength 2"
            ],
            "penalties_applied": [
                "Penalty 1: -X points for reason",
                "Penalty 2: -X points for reason"
            ],
            "bonuses_applied": [
                "Bonus 1: +X points for reason",
                "Bonus 2: +X points for reason"
            ],
            "recommendation": "Invest / Don't invest / More research needed / Pass",
            "critical_concerns": [
                "Critical concern 1 that must be addressed",
                "Critical concern 2 that must be addressed"
            ]
        }}
        
        Be extremely critical and objective. If the team is weak, market is small, or risks are high, score accordingly. Don't be generous with scores.
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
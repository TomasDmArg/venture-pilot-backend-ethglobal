from openai import OpenAI
import logging
from typing import Dict, Any
from app.core.config import settings

# Setup logging
logger = logging.getLogger(__name__)

class SummaryGenerator:
    def __init__(self):
        if not settings.openai_api_key:
            raise ValueError("OpenAI API key not configured")
        
        self.client = OpenAI(api_key=settings.openai_api_key)
    
    async def generate_simple_summary(self, project_info: Dict[str, Any], viability_score: int) -> str:
        """
        Generate an ultra-simple summary (1 line max) in English
        """
        try:
            logger.info(f"Generating summary for project: {project_info.get('project_name', 'Unknown')}")
            
            prompt = f"""
            Generate an ULTRA SIMPLE one-line summary of this project in English.
            
            PROJECT INFO:
            - Name: {project_info.get('project_name', 'N/A')}
            - Description: {project_info.get('description', 'N/A')}
            - Market: {project_info.get('target_market', 'N/A')}
            - Team: {len(project_info.get('team_info', []))} members
            - Viability: {viability_score}/10
            
            Requirements:
            - Maximum 1 line (not 2)
            - Include what the project does
            - Mention target market
            - Include viability score
            - Be concise and clear
            - ALWAYS in English regardless of input language
            
            Example: "AI-powered startup analysis platform for VCs and accelerators. Viability: 8/10"
            
            Summary:
            """
            
            logger.info("Generating summary with OpenAI...")
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert at creating concise one-line business summaries in English."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )
            
            summary = response.choices[0].message.content or "Summary not available"
            
            # Clean up the summary
            summary = summary.strip()
            if summary.startswith("Summary:"):
                summary = summary[8:].strip()
            
            # Remove extra quotes
            if summary.startswith('"') and summary.endswith('"'):
                summary = summary[1:-1]
            
            # Ensure it's one line
            summary = summary.replace('\n', ' ').replace('\r', ' ')
            
            logger.info(f"Summary generated: {summary}")
            return summary
            
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            return f"Error generating summary: {str(e)}" 
from openai import OpenAI
from typing import Dict, Any
from app.core.config import settings

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
            # Create assessment prompt
            prompt = self._create_viability_prompt(project_info)
            
            # Get assessment from OpenAI
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert VC analyst. Provide clear, objective viability assessments."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )
            
            assessment_text = response.choices[0].message.content or ""
            
            # Parse the assessment
            return self._parse_viability_assessment(assessment_text)
            
        except Exception as e:
            return {
                "score": 5,
                "explanation": f"Error en evaluación: {str(e)}",
                "risk_factors": ["Error técnico"],
                "strengths": []
            }
    
    def _create_viability_prompt(self, project_info: Dict[str, Any]) -> str:
        """
        Create viability assessment prompt
        """
        return f"""
        Evalúa la viabilidad de este proyecto desde la perspectiva de un VC (Venture Capital).
        
        INFORMACIÓN DEL PROYECTO:
        - Nombre: {project_info.get('project_name', 'N/A')}
        - Descripción: {project_info.get('description', 'N/A')}
        - Problema: {project_info.get('problem_statement', 'N/A')}
        - Solución: {project_info.get('solution', 'N/A')}
        - Mercado objetivo: {project_info.get('target_market', 'N/A')}
        - Modelo de negocio: {project_info.get('business_model', 'N/A')}
        - Equipo: {project_info.get('team_info', [])}
        
        CRITERIOS DE EVALUACIÓN (1-10):
        1-2: Muy alto riesgo, mercado dudoso, equipo débil
        3-4: Alto riesgo, problemas significativos
        5-6: Riesgo medio, potencial limitado
        7-8: Bajo riesgo, buen potencial
        9-10: Muy bajo riesgo, excelente potencial
        
        Proporciona tu evaluación en este formato JSON:
        {{
            "score": 8,
            "explanation": "Explicación clara y concisa de por qué este puntaje",
            "risk_factors": [
                "Factor de riesgo 1",
                "Factor de riesgo 2"
            ],
            "strengths": [
                "Fortaleza 1",
                "Fortaleza 2"
            ],
            "recommendation": "Invertir / No invertir / Más investigación"
        }}
        
        Sé objetivo y específico. Considera: tamaño del mercado, competencia, equipo, tecnología, escalabilidad, y modelo de negocio.
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
                "risk_factors": ["Análisis incompleto"],
                "strengths": [],
                "recommendation": "Más investigación"
            }
            
        except Exception as e:
            return {
                "score": 5,
                "explanation": f"Error parsing assessment: {str(e)}",
                "risk_factors": ["Error técnico"],
                "strengths": [],
                "recommendation": "Más investigación"
            } 
import logging
from typing import List, Dict, Any
from openai import OpenAI
from app.core.config import settings

# Setup logging
logger = logging.getLogger(__name__)

class ComplianceAgent:
    def __init__(self):
        if not settings.openai_api_key:
            raise ValueError("OpenAI API key not configured")
        
        self.client = OpenAI(api_key=settings.openai_api_key)
    
    async def analyze_compliance_risks(self, project_info: Dict[str, Any], founders: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze compliance and regulatory risks for the project
        """
        try:
            logger.info(f"Starting compliance analysis for: {project_info.get('project_name', 'Unknown')}")
            
            # Create comprehensive compliance analysis prompt
            prompt = self._create_compliance_prompt(project_info, founders)
            
            # Generate compliance analysis with OpenAI
            logger.info("Generating compliance analysis with OpenAI...")
            response = self.client.chat.completions.create(
                model="gpt-5-nano-2025-08-07",
                messages=[
                    {"role": "system", "content": "You are an expert compliance and regulatory analyst specializing in startup evaluation. Identify all potential legal, regulatory, and compliance risks."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )
            
            analysis_text = response.choices[0].message.content or ""
            logger.info("Compliance analysis generated successfully")
            
            # Parse compliance analysis
            compliance_analysis = self._parse_compliance_analysis(analysis_text)
            
            return {
                "compliance_risks": compliance_analysis.get("compliance_risks", []),
                "regulatory_requirements": compliance_analysis.get("regulatory_requirements", []),
                "legal_risks": compliance_analysis.get("legal_risks", []),
                "data_privacy_concerns": compliance_analysis.get("data_privacy_concerns", []),
                "compliance_score": compliance_analysis.get("compliance_score", 5),
                "risk_level": compliance_analysis.get("risk_level", "medium"),
                "recommendations": compliance_analysis.get("recommendations", []),
                "required_licenses": compliance_analysis.get("required_licenses", []),
                "jurisdictions": compliance_analysis.get("jurisdictions", [])
            }
            
        except Exception as e:
            logger.error(f"Error in compliance analysis: {str(e)}")
            return {
                "compliance_risks": [f"Error in analysis: {str(e)}"],
                "regulatory_requirements": [],
                "legal_risks": [],
                "data_privacy_concerns": [],
                "compliance_score": 5,
                "risk_level": "unknown",
                "recommendations": ["Consult with legal experts"],
                "required_licenses": [],
                "jurisdictions": []
            }
    
    def _create_compliance_prompt(self, project_info: Dict[str, Any], founders: List[Dict[str, Any]]) -> str:
        """
        Create comprehensive prompt for compliance analysis
        """
        return f"""
        Analyze the compliance and regulatory risks for this startup project. Consider all potential legal, regulatory, and compliance issues.
        
        PROJECT INFORMATION:
        - Name: {project_info.get('project_name', 'N/A')}
        - Description: {project_info.get('description', 'N/A')}
        - Problem: {project_info.get('problem_statement', 'N/A')}
        - Solution: {project_info.get('solution', 'N/A')}
        - Target Market: {project_info.get('target_market', 'N/A')}
        - Business Model: {project_info.get('business_model', 'N/A')}
        
        FOUNDERS ({len(founders)}):
        {self._format_founders_for_compliance(founders)}
        
        COMPLIANCE AREAS TO ANALYZE:
        1. Data Privacy & GDPR/CCPA compliance
        2. Financial regulations (if applicable)
        3. Industry-specific regulations
        4. Intellectual property risks
        5. Employment law compliance
        6. International trade regulations
        7. Environmental regulations
        8. Consumer protection laws
        9. Cybersecurity regulations
        10. Tax compliance requirements
        
        Please provide your analysis in this JSON format:
        {{
            "compliance_score": 7.5,
            "risk_level": "high/medium/low",
            "compliance_risks": [
                {{
                    "risk": "Specific compliance risk description",
                    "severity": "high/medium/low",
                    "impact": "Potential impact on business",
                    "mitigation": "How to mitigate this risk"
                }}
            ],
            "regulatory_requirements": [
                "Specific regulatory requirement 1",
                "Specific regulatory requirement 2"
            ],
            "legal_risks": [
                {{
                    "risk": "Legal risk description",
                    "probability": "high/medium/low",
                    "consequences": "Potential legal consequences"
                }}
            ],
            "data_privacy_concerns": [
                "Data privacy concern 1",
                "Data privacy concern 2"
            ],
            "recommendations": [
                "Compliance recommendation 1",
                "Compliance recommendation 2"
            ],
            "required_licenses": [
                "License or permit required 1",
                "License or permit required 2"
            ],
            "jurisdictions": [
                "Primary jurisdiction 1",
                "Secondary jurisdiction 2"
            ]
        }}
        
        Be thorough and consider all potential compliance issues. Focus on high-impact risks that could significantly affect the business.
        """
    
    def _format_founders_for_compliance(self, founders: List[Dict[str, Any]]) -> str:
        """
        Format founders information for compliance analysis
        """
        if not founders:
            return "No founder information available"
        
        formatted = []
        for i, founder in enumerate(founders[:3], 1):  # Limit to top 3
            name = founder.get('name', 'Unknown')
            role = founder.get('role', 'Unknown role')
            score = founder.get('score', 'N/A')
            formatted.append(f"{i}. {name} ({role}) - Score: {score}/10")
        
        return "\n".join(formatted)
    
    def _parse_compliance_analysis(self, analysis_text: str) -> Dict[str, Any]:
        """
        Parse compliance analysis from OpenAI response
        """
        try:
            import json
            import re
            
            logger.info(f"Raw compliance analysis response: {analysis_text[:200]}...")
            
            # Strategy 1: Try to find JSON block with regex
            try:
                json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', analysis_text, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                    logger.info(f"Found JSON block: {json_str[:100]}...")
                    analysis = json.loads(json_str)
                    return self._validate_compliance_analysis(analysis)
            except Exception as e:
                logger.warning(f"Strategy 1 failed: {str(e)}")
            
            # Strategy 2: Try to extract JSON from the entire text
            try:
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
                        return self._validate_compliance_analysis(analysis)
            except Exception as e:
                logger.warning(f"Strategy 2 failed: {str(e)}")
            
            # Strategy 3: Try to parse the entire text as JSON
            try:
                analysis = json.loads(analysis_text.strip())
                return self._validate_compliance_analysis(analysis)
            except Exception as e:
                logger.warning(f"Strategy 3 failed: {str(e)}")
            
            # Strategy 4: Manual extraction from text
            try:
                analysis = self._extract_compliance_analysis_manually(analysis_text)
                return self._validate_compliance_analysis(analysis)
            except Exception as e:
                logger.warning(f"Strategy 4 failed: {str(e)}")
            
            # Final fallback
            logger.warning("All JSON parsing strategies failed, using fallback")
            return {
                "compliance_score": 5,
                "risk_level": "medium",
                "compliance_risks": ["Analysis incomplete - consult legal experts"],
                "regulatory_requirements": [],
                "legal_risks": [],
                "data_privacy_concerns": [],
                "recommendations": ["Seek legal counsel for comprehensive compliance review"],
                "required_licenses": [],
                "jurisdictions": []
            }
            
        except Exception as e:
            logger.error(f"Error parsing compliance analysis: {str(e)}")
            return {
                "compliance_score": 5,
                "risk_level": "unknown",
                "compliance_risks": [f"Error parsing analysis: {str(e)}"],
                "regulatory_requirements": [],
                "legal_risks": [],
                "data_privacy_concerns": [],
                "recommendations": ["Consult with legal experts"],
                "required_licenses": [],
                "jurisdictions": []
            }
    
    def _validate_compliance_analysis(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and clean compliance analysis data
        """
        return {
            "compliance_score": analysis.get("compliance_score", 5),
            "risk_level": analysis.get("risk_level", "medium"),
            "compliance_risks": analysis.get("compliance_risks", []) if isinstance(analysis.get("compliance_risks"), list) else [],
            "regulatory_requirements": analysis.get("regulatory_requirements", []) if isinstance(analysis.get("regulatory_requirements"), list) else [],
            "legal_risks": analysis.get("legal_risks", []) if isinstance(analysis.get("legal_risks"), list) else [],
            "data_privacy_concerns": analysis.get("data_privacy_concerns", []) if isinstance(analysis.get("data_privacy_concerns"), list) else [],
            "recommendations": analysis.get("recommendations", []) if isinstance(analysis.get("recommendations"), list) else [],
            "required_licenses": analysis.get("required_licenses", []) if isinstance(analysis.get("required_licenses"), list) else [],
            "jurisdictions": analysis.get("jurisdictions", []) if isinstance(analysis.get("jurisdictions"), list) else []
        }
    
    def _extract_compliance_analysis_manually(self, text: str) -> Dict[str, Any]:
        """
        Manually extract compliance analysis from text if JSON parsing fails
        """
        analysis = {
            "compliance_score": 5,
            "risk_level": "medium",
            "compliance_risks": [],
            "regulatory_requirements": [],
            "legal_risks": [],
            "data_privacy_concerns": [],
            "recommendations": ["Manual analysis required"],
            "required_licenses": [],
            "jurisdictions": []
        }
        
        # Try to extract compliance score
        score_match = re.search(r'"compliance_score":\s*(\d+(?:\.\d+)?)', text)
        if score_match:
            try:
                analysis["compliance_score"] = float(score_match.group(1))
            except:
                pass
        
        # Try to extract risk level
        if "high" in text.lower() and "risk" in text.lower():
            analysis["risk_level"] = "high"
        elif "low" in text.lower() and "risk" in text.lower():
            analysis["risk_level"] = "low"
        
        # Try to extract compliance risks
        lines = text.split('\n')
        for line in lines:
            if "risk" in line.lower() and len(line.strip()) > 10:
                analysis["compliance_risks"].append(line.strip())
        
        return analysis 
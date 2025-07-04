import logging
from typing import List, Dict, Any
from openai import OpenAI
from app.core.config import settings

# Setup logging
logger = logging.getLogger(__name__)

class FollowUpAgent:
    def __init__(self):
        if not settings.openai_api_key:
            raise ValueError("OpenAI API key not configured")
        
        self.client = OpenAI(api_key=settings.openai_api_key)
    
    async def generate_followup_questions(self, project_info: Dict[str, Any], founders: List[Dict[str, Any]], viability_assessment: Dict[str, Any], competitor_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate 10 top-tier follow-up questions for the project
        """
        try:
            logger.info(f"Generating follow-up questions for: {project_info.get('project_name', 'Unknown')}")
            
            # Create comprehensive prompt for question generation
            prompt = self._create_question_prompt(project_info, founders, viability_assessment, competitor_analysis)
            
            # Generate questions with OpenAI
            logger.info("Generating follow-up questions with OpenAI...")
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert VC analyst who asks the most critical questions to evaluate startups. Generate only the most important, penetrating questions that will reveal the true potential and risks of a project."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )
            
            questions_text = response.choices[0].message.content or ""
            logger.info("Follow-up questions generated successfully")
            
            # Parse and categorize questions
            questions = self._parse_and_categorize_questions(questions_text)
            
            return {
                "followup_questions": questions,
                "total_questions": len(questions),
                "categories": self._get_question_categories(questions),
                "priority_questions": questions[:3] if len(questions) >= 3 else questions
            }
            
        except Exception as e:
            logger.error(f"Error generating follow-up questions: {str(e)}")
            return {
                "followup_questions": [{"question": f"Error generating questions: {str(e)}", "category": "error"}],
                "total_questions": 1,
                "categories": ["error"],
                "priority_questions": []
            }
    
    def _create_question_prompt(self, project_info: Dict[str, Any], founders: List[Dict[str, Any]], viability_assessment: Dict[str, Any], competitor_analysis: Dict[str, Any]) -> str:
        """
        Create comprehensive prompt for generating follow-up questions
        """
        return f"""
        Generate exactly 10 CRITICAL follow-up questions for this startup project. These should be the most important questions a VC would ask to evaluate the investment potential.
        
        PROJECT INFORMATION:
        - Name: {project_info.get('project_name', 'N/A')}
        - Description: {project_info.get('description', 'N/A')}
        - Problem: {project_info.get('problem_statement', 'N/A')}
        - Solution: {project_info.get('solution', 'N/A')}
        - Target Market: {project_info.get('target_market', 'N/A')}
        - Business Model: {project_info.get('business_model', 'N/A')}
        
        FOUNDERS ({len(founders)}):
        {self._format_founders_for_questions(founders)}
        
        VIABILITY ASSESSMENT:
        - Score: {viability_assessment.get('score', 'N/A')}/10
        - Risk Factors: {viability_assessment.get('risk_factors', [])}
        - Strengths: {viability_assessment.get('strengths', [])}
        
        COMPETITIVE LANDSCAPE:
        - Threat Level: {competitor_analysis.get('threat_level', 'N/A')}
        - Market Saturation: {competitor_analysis.get('market_saturation', 'N/A')}
        - Competitive Advantage: {competitor_analysis.get('competitive_advantage', 'N/A')}
        
        REQUIREMENTS:
        - Generate exactly 10 questions
        - Each question should be specific and actionable
        - Focus on the most critical areas: team, market, technology, business model, competition, execution
        - Questions should reveal potential red flags or confirm strengths
        - Be direct and challenging - these are for serious due diligence
        
        CATEGORIES TO COVER:
        1. Team & Execution (2-3 questions)
        2. Market & Competition (2-3 questions)
        3. Technology & Product (2-3 questions)
        4. Business Model & Financials (2-3 questions)
        5. Risk & Mitigation (1-2 questions)
        
        Return the questions in this JSON format:
        [
            {{
                "question": "Specific, challenging question here?",
                "category": "team|market|technology|business|risk",
                "priority": "high|medium|low",
                "rationale": "Why this question is critical"
            }}
        ]
        
        Make these questions count - they should be the questions that separate good investments from bad ones.
        """
    
    def _format_founders_for_questions(self, founders: List[Dict[str, Any]]) -> str:
        """
        Format founders information for question generation
        """
        if not founders:
            return "No founder information available"
        
        formatted = []
        for i, founder in enumerate(founders[:3], 1):  # Limit to top 3
            score = founder.get('score', 'N/A')
            role = founder.get('role', 'Unknown role')
            formatted.append(f"{i}. {founder.get('name', 'Unknown')} ({role}) - Score: {score}/10")
        
        return "\n".join(formatted)
    
    def _parse_and_categorize_questions(self, questions_text: str) -> List[Dict[str, Any]]:
        """
        Parse questions from OpenAI response and categorize them
        """
        try:
            import json
            import re
            
            logger.info(f"Raw follow-up questions response: {questions_text[:200]}...")
            
            # Strategy 1: Try to find JSON array with regex
            try:
                json_match = re.search(r'\[[^\[\]]*(?:\{[^{}]*\}[^\[\]]*)*\]', questions_text, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                    logger.info(f"Found JSON array: {json_str[:100]}...")
                    questions = json.loads(json_str)
                    return self._validate_questions(questions)
            except Exception as e:
                logger.warning(f"Strategy 1 failed: {str(e)}")
            
            # Strategy 2: Try to extract JSON from the entire text
            try:
                start_idx = questions_text.find('[')
                if start_idx != -1:
                    json_str = questions_text[start_idx:]
                    # Find the matching closing bracket
                    bracket_count = 0
                    end_idx = -1
                    for i, char in enumerate(json_str):
                        if char == '[':
                            bracket_count += 1
                        elif char == ']':
                            bracket_count -= 1
                            if bracket_count == 0:
                                end_idx = i + 1
                                break
                    
                    if end_idx != -1:
                        json_str = json_str[:end_idx]
                        logger.info(f"Extracted JSON: {json_str[:100]}...")
                        questions = json.loads(json_str)
                        return self._validate_questions(questions)
            except Exception as e:
                logger.warning(f"Strategy 2 failed: {str(e)}")
            
            # Strategy 3: Try to parse the entire text as JSON
            try:
                questions = json.loads(questions_text.strip())
                return self._validate_questions(questions)
            except Exception as e:
                logger.warning(f"Strategy 3 failed: {str(e)}")
            
            # Strategy 4: Manual extraction from text
            try:
                questions = self._extract_questions_manually(questions_text)
                return self._validate_questions(questions)
            except Exception as e:
                logger.warning(f"Strategy 4 failed: {str(e)}")
            
            # Final fallback
            logger.warning("All JSON parsing strategies failed, using fallback")
            return self._generate_fallback_questions()
            
        except Exception as e:
            logger.error(f"Error parsing follow-up questions: {str(e)}")
            return self._generate_fallback_questions()
    
    def _validate_questions(self, questions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Validate and clean questions data
        """
        valid_questions = []
        for q in questions:
            if isinstance(q, dict) and q.get('question'):
                valid_questions.append({
                    "question": q.get('question', '').strip(),
                    "category": q.get('category', 'general'),
                    "priority": q.get('priority', 'medium'),
                    "rationale": q.get('rationale', 'No rationale provided')
                })
        
        return valid_questions[:10]  # Ensure max 10 questions
    
    def _generate_fallback_questions(self) -> List[Dict[str, Any]]:
        """
        Generate fallback questions when parsing fails
        """
        return [
            {
                "question": "What is your team's relevant experience in this industry?",
                "category": "team",
                "priority": "high",
                "rationale": "Team experience is critical for success"
            },
            {
                "question": "What is your total addressable market (TAM) and how did you calculate it?",
                "category": "market",
                "priority": "high",
                "rationale": "Market size determines investment potential"
            },
            {
                "question": "What is your unique competitive advantage or moat?",
                "category": "technology",
                "priority": "high",
                "rationale": "Competitive advantage is essential for long-term success"
            },
            {
                "question": "How do you plan to generate revenue and what are your unit economics?",
                "category": "business",
                "priority": "medium",
                "rationale": "Business model viability is crucial"
            },
            {
                "question": "What are your biggest risks and how do you plan to mitigate them?",
                "category": "risk",
                "priority": "medium",
                "rationale": "Risk assessment is important for investment decision"
            }
        ]
    
    def _extract_questions_manually(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract questions manually from text if JSON parsing fails
        """
        questions = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if line and ('?' in line or line.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '10.'))):
                # Clean up the question
                question = line
                if line.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '10.')):
                    question = line[line.find('.')+1:].strip()
                
                if question and len(question) > 10:
                    questions.append({
                        "question": question,
                        "category": self._categorize_question(question),
                        "priority": "medium",
                        "rationale": "Extracted from response"
                    })
        
        return questions[:10]
    
    def _categorize_question(self, question: str) -> str:
        """
        Automatically categorize a question based on keywords
        """
        question_lower = question.lower()
        
        team_keywords = ['team', 'founder', 'experience', 'background', 'execution', 'leadership']
        market_keywords = ['market', 'competition', 'customer', 'demand', 'size', 'growth']
        tech_keywords = ['technology', 'product', 'development', 'technical', 'platform', 'ai', 'ml']
        business_keywords = ['revenue', 'business model', 'pricing', 'cost', 'financial', 'funding']
        risk_keywords = ['risk', 'challenge', 'problem', 'obstacle', 'threat']
        
        if any(keyword in question_lower for keyword in team_keywords):
            return "team"
        elif any(keyword in question_lower for keyword in market_keywords):
            return "market"
        elif any(keyword in question_lower for keyword in tech_keywords):
            return "technology"
        elif any(keyword in question_lower for keyword in business_keywords):
            return "business"
        elif any(keyword in question_lower for keyword in risk_keywords):
            return "risk"
        else:
            return "general"
    
    def _get_question_categories(self, questions: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Get count of questions by category
        """
        categories = {}
        for q in questions:
            category = q.get('category', 'general')
            categories[category] = categories.get(category, 0) + 1
        return categories 
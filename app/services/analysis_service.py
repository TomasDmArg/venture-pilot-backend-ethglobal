import base64
import io
from typing import List, Dict, Any, Optional
from crewai import Agent, Task, Crew, Process
from app.core.config import settings
from app.models.schemas import ProjectSummary, FounderInfo, GitRollScan
from app.services.founder_search_service import FounderSearchService
from app.services.gitroll_service import GitRollService
import asyncio
from pydantic import SecretStr

class AnalysisService:
    def __init__(self):
        self.founder_search_service = FounderSearchService()
        self.gitroll_service = GitRollService()
        
    async def analyze_project(self, deck_file: str, project_name: Optional[str] = None) -> ProjectSummary:
        """
        Main analysis function using CrewAI multiagent system
        """
        # Decode base64 deck file
        deck_content = self._decode_deck_file(deck_file)
        
        # Create CrewAI agents
        deck_analyzer = self._create_deck_analyzer_agent()
        founder_researcher = self._create_founder_researcher_agent()
        github_analyzer = self._create_github_analyzer_agent()
        
        # Create tasks
        deck_analysis_task = self._create_deck_analysis_task(deck_analyzer, deck_content, project_name)
        founder_research_task = self._create_founder_research_task(founder_researcher)
        github_analysis_task = self._create_github_analysis_task(github_analyzer)
        
        # Create and run crew
        crew = Crew(
            agents=[deck_analyzer, founder_researcher, github_analyzer],
            tasks=[deck_analysis_task, founder_research_task, github_analysis_task],
            process=Process.sequential,
            verbose=True
        )
        
        result = crew.kickoff()
        
        # Parse results and create project summary
        return await self._parse_crew_results(result)
    
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
    
    def _create_deck_analyzer_agent(self) -> Agent:
        """
        Create agent for analyzing project decks
        """
        return Agent(
            role='Project Deck Analyst',
            goal='Analyze project decks to extract key business information',
            backstory="""You are an expert business analyst specializing in startup and project evaluation. 
            You have years of experience analyzing pitch decks, business plans, and project documentation. 
            You can quickly identify the core value proposition, market opportunity, business model, and team structure.""",
            verbose=True,
            allow_delegation=False,
            tools=[],
            llm=self._get_llm()
        )
    
    def _create_founder_researcher_agent(self) -> Agent:
        """
        Create agent for researching founders
        """
        return Agent(
            role='Founder Research Specialist',
            goal='Research and find information about project founders and team members',
            backstory="""You are a skilled researcher specializing in finding information about startup founders 
            and team members. You know how to search across multiple platforms including LinkedIn, Twitter, 
            GitHub, and other professional networks to gather comprehensive information about individuals.""",
            verbose=True,
            allow_delegation=False,
            tools=[],
            llm=self._get_llm()
        )
    
    def _create_github_analyzer_agent(self) -> Agent:
        """
        Create agent for analyzing GitHub repositories
        """
        return Agent(
            role='GitHub Repository Analyst',
            goal='Analyze GitHub repositories to understand project technical implementation and team contributions',
            backstory="""You are a technical analyst with deep expertise in software development and GitHub. 
            You can analyze repository structures, code quality, contribution patterns, and technical architecture 
            to understand the technical capabilities and development practices of a project team.""",
            verbose=True,
            allow_delegation=False,
            tools=[],
            llm=self._get_llm()
        )
    
    def _create_deck_analysis_task(self, agent: Agent, deck_content: str, project_name: Optional[str]) -> Task:
        """
        Create task for deck analysis
        """
        return Task(
            description=f"""
            Analyze the provided project deck content and extract the following information:
            
            1. Project Name: {project_name or 'Extract from deck'}
            2. Project Description: A clear, concise description of what the project does
            3. Problem Statement: What problem is the project trying to solve
            4. Solution: How does the project solve the identified problem
            5. Target Market: Who are the target customers/users
            6. Business Model: How does the project generate revenue
            7. Team Information: Names and roles of key team members/founders
            
            Deck Content:
            {deck_content[:2000]}...
            
            Provide your analysis in a structured JSON format with the following fields:
            - project_name
            - description
            - problem_statement
            - solution
            - target_market
            - business_model
            - team_members (list of names)
            """,
            agent=agent,
            expected_output="JSON formatted analysis of the project deck"
        )
    
    def _create_founder_research_task(self, agent: Agent) -> Task:
        """
        Create task for founder research
        """
        return Task(
            description="""
            Based on the project analysis, research the founders and team members to find:
            
            1. LinkedIn profiles
            2. Twitter/X profiles
            3. GitHub usernames
            4. Professional background and experience
            5. Previous companies or projects
            
            For each founder/team member found, provide:
            - Full name
            - LinkedIn URL (if found)
            - Twitter URL (if found)
            - GitHub username (if found)
            - Brief bio/background
            - Current company
            - Location
            
            Provide results in JSON format with an array of founder objects.
            """,
            agent=agent,
            expected_output="JSON formatted list of founder information"
        )
    
    def _create_github_analysis_task(self, agent: Agent) -> Task:
        """
        Create task for GitHub analysis
        """
        return Task(
            description="""
            Analyze the GitHub repositories associated with the project and founders to:
            
            1. Identify relevant repositories
            2. Analyze code quality and activity
            3. Understand technical stack and architecture
            4. Evaluate team's technical capabilities
            5. Identify key contributors and their roles
            
            For each relevant repository, provide:
            - Repository name and URL
            - Primary programming languages
            - Activity level (commits, issues, etc.)
            - Key contributors
            - Project maturity indicators
            
            Provide results in JSON format with repository analysis.
            """,
            agent=agent,
            expected_output="JSON formatted GitHub repository analysis"
        )
    
    def _get_llm(self):
        """
        Get OpenAI LLM configuration
        """
        from langchain_openai import ChatOpenAI
        
        if not settings.openai_api_key:
            raise ValueError("OpenAI API key not configured. Please set OPENAI_API_KEY in your .env file")
        
        return ChatOpenAI(
            model="gpt-5-nano-2025-08-07",
            api_key=settings.openai_api_key,
            temperature=1
        )
    
    async def _parse_crew_results(self, result: str) -> ProjectSummary:
        """
        Parse CrewAI results and create ProjectSummary
        """
        try:
            # This is a simplified parser - in production you'd want more robust JSON parsing
            # For now, we'll create a basic structure
            
            # Extract project information from the result
            project_info = self._extract_project_info(result)
            
            # Search for founders
            founders = await self.founder_search_service.search_founders(
                project_info.get('project_name', ''),
                project_info.get('company_name', '')
            )
            
            # Get GitHub repositories
            github_repos = self._extract_github_repos(result)
            
            # Initiate GitRoll scans for founders with GitHub usernames
            gitroll_scans = []
            for founder in founders:
                if founder.github_username:
                    scan_result = await self.gitroll_service.initiate_scan(founder.github_username)
                    if scan_result.success:
                        gitroll_scan = GitRollScan(
                            username=founder.github_username,
                            scan_id=scan_result.scan_id,
                            profile_url=scan_result.profile_url,
                            status="initiated"
                        )
                        gitroll_scans.append(gitroll_scan)
            
            return ProjectSummary(
                project_name=project_info.get('project_name', 'Unknown Project'),
                description=project_info.get('description', ''),
                problem_statement=project_info.get('problem_statement', ''),
                solution=project_info.get('solution', ''),
                target_market=project_info.get('target_market', ''),
                business_model=project_info.get('business_model', ''),
                team_info=founders,
                github_repos=github_repos,
                gitroll_scans=gitroll_scans
            )
            
        except Exception as e:
            # Return a basic summary if parsing fails
            return ProjectSummary(
                project_name="Analysis Failed",
                description=f"Error parsing results: {str(e)}",
                problem_statement="",
                solution="",
                target_market="",
                business_model="",
                team_info=[],
                github_repos=[],
                gitroll_scans=[]
            )
    
    def _extract_project_info(self, result: str) -> Dict[str, str]:
        """
        Extract project information from CrewAI result
        """
        # This is a simplified extraction - in production you'd want more robust parsing
        info = {}
        
        # Look for JSON-like structures in the result
        import re
        import json
        
        # Try to find JSON blocks
        json_pattern = r'\{[^{}]*"project_name"[^{}]*\}'
        matches = re.findall(json_pattern, result, re.DOTALL)
        
        if matches:
            try:
                parsed = json.loads(matches[0])
                info.update(parsed)
            except:
                pass
        
        # Fallback: extract basic information using regex
        if 'project_name' not in info:
            name_match = re.search(r'project_name["\s:]+([^"\n,}]+)', result, re.IGNORECASE)
            if name_match:
                info['project_name'] = name_match.group(1).strip()
        
        return info
    
    def _extract_github_repos(self, result: str) -> List[str]:
        """
        Extract GitHub repository URLs from CrewAI result
        """
        import re
        
        # Look for GitHub URLs
        github_pattern = r'https://github\.com/[a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+'
        repos = re.findall(github_pattern, result)
        
        return list(set(repos))  # Remove duplicates 
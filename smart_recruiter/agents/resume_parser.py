"""Resume Parser Agent - Extracts information from resumes."""
from crewai import Agent
from ..tools import ResumeParserTool, ResumeAnalyzerTool
from ..config.settings import settings

def create_resume_parser_agent() -> Agent:
    """Create the Resume Parser Agent."""
    return Agent(
        role="Resume Parser",
        goal="""Parse resumes accurately and extract all relevant information
        including contact details, skills, experience, and education.""",
        backstory="""You are an expert resume analyst with extensive experience
        in HR technology. You've processed over 100,000 resumes and can quickly
        identify key information regardless of the resume format. You understand
        various resume styles and can extract data from traditional, creative,
        and technical resumes alike.""",
        tools=[ResumeParserTool(), ResumeAnalyzerTool()],
        verbose=True,
        allow_delegation=False,
        llm=f"groq/{settings.groq_model}",
    )


def create_resume_reviewer_agent() -> Agent:
    """Create the Resume Reviewer Agent for quality assessment."""
    return Agent(
        role="Resume Quality Reviewer",
        goal="""Review parsed resume data for completeness and accuracy,
        identifying any gaps or inconsistencies that may affect screening.""",
        backstory="""You are a senior recruiter with a sharp eye for detail.
        You've seen every trick in the book - embellished titles, vague
        responsibilities, and gaps in employment. You can quickly assess
        the quality and authenticity of resume information.""",
        tools=[ResumeAnalyzerTool()],
        verbose=True,
        allow_delegation=False,
        llm=f"groq/{settings.groq_model}",
    )

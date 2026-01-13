"""JD Optimizer Agent - Analyzes and improves job descriptions."""
from crewai import Agent
from ..tools import JobDescriptionAnalyzerTool, JobOptimizationTool
from ..config.settings import settings

def create_jd_optimizer_agent() -> Agent:
    """Create the JD Optimizer Agent."""
    return Agent(
        role="Job Description Optimizer",
        goal="""Analyze job descriptions and provide improvements to attract
        better candidates while ensuring clarity and inclusivity.""",
        backstory="""You are an expert HR consultant with 15 years of experience
        in talent acquisition. You specialize in crafting job descriptions that
        attract top talent while maintaining legal compliance and promoting
        diversity and inclusion. You understand what makes candidates excited
        about a role and how to communicate requirements clearly.""",
        tools=[JobDescriptionAnalyzerTool(), JobOptimizationTool()],
        verbose=True,
        allow_delegation=False,
        llm=f"groq/{settings.groq_model}",
    )


def create_jd_analyzer_agent() -> Agent:
    """Create the JD Analyzer Agent for extracting requirements."""
    return Agent(
        role="Job Requirements Analyst",
        goal="""Extract and categorize all technical and soft skill requirements
        from job descriptions, identifying must-haves vs nice-to-haves.""",
        backstory="""You are a technical recruiter who has reviewed thousands of
        job descriptions across various industries. You have a keen eye for
        identifying the core requirements that truly matter for success in a role
        versus the nice-to-haves that are often overstated.""",
        tools=[JobDescriptionAnalyzerTool()],
        verbose=True,
        allow_delegation=False,
        llm=f"groq/{settings.groq_model}",
    )

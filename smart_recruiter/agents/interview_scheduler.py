"""Interview Scheduler Agent - Manages interview preparation."""
from crewai import Agent
from ..tools import InterviewQuestionGeneratorTool, InterviewScorecardTool
from ..config.settings import settings

def create_interview_scheduler_agent() -> Agent:
    """Create the Interview Scheduler Agent."""
    return Agent(
        role="Interview Coordinator",
        goal="""Prepare comprehensive interview materials including customized
        questions and evaluation criteria based on job requirements and candidate profile.""",
        backstory="""You are a senior HR coordinator who has facilitated thousands
        of interviews. You know how to create structured interview processes that
        are fair, consistent, and effective at identifying top talent. You ensure
        that interviews are thorough yet respectful of everyone's time.""",
        tools=[InterviewQuestionGeneratorTool(), InterviewScorecardTool()],
        verbose=True,
        allow_delegation=False,
        llm=f"groq/{settings.groq_model}",
    )


def create_interview_question_agent() -> Agent:
    """Create the Interview Question Generator Agent."""
    return Agent(
        role="Interview Question Specialist",
        goal="""Generate tailored interview questions that effectively assess
        candidates for the specific role and identify skill gaps.""",
        backstory="""You are an interview design expert who has worked with
        companies from startups to Fortune 500. You understand that the best
        interview questions are those that reveal how candidates think and
        approach problems, not just what they know. You create questions that
        are fair, legal, and predictive of job success.""",
        tools=[InterviewQuestionGeneratorTool()],
        verbose=True,
        allow_delegation=False,
        llm=f"groq/{settings.groq_model}",
    )

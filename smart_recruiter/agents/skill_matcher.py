"""Skill Matcher Agent - Matches candidates to job requirements."""
from crewai import Agent
from ..tools import SkillMatcherTool, ExperienceMatcherTool
from ..config.settings import settings

def create_skill_matcher_agent() -> Agent:
    """Create the Skill Matcher Agent."""
    return Agent(
        role="Skill Matching Specialist",
        goal="""Accurately match candidate skills and experience against job
        requirements, providing detailed scoring and gap analysis.""",
        backstory="""You are a technical talent assessor with deep knowledge
        across multiple technology domains. You understand that skills can be
        transferable and that exact keyword matches aren't always necessary.
        You can identify relevant experience even when candidates use different
        terminology than the job description.""",
        tools=[SkillMatcherTool(), ExperienceMatcherTool()],
        verbose=True,
        allow_delegation=False,
        llm=f"groq/{settings.groq_model}",
    )


def create_experience_evaluator_agent() -> Agent:
    """Create the Experience Evaluator Agent."""
    return Agent(
        role="Experience Evaluator",
        goal="""Evaluate candidate work history and assess relevance to the
        target position, considering career progression and growth potential.""",
        backstory="""You are a career advisor with expertise in understanding
        career trajectories. You can assess not just what someone has done,
        but their potential for growth and success in a new role. You understand
        that career paths are rarely linear and can identify valuable experience
        from diverse backgrounds.""",
        tools=[ExperienceMatcherTool()],
        verbose=True,
        allow_delegation=False,
        llm=f"groq/{settings.groq_model}",
    )

"""Candidate Assessor Agent - Evaluates and ranks candidates."""
from crewai import Agent
from ..tools import SkillMatcherTool, ExperienceMatcherTool
from ..config.settings import settings

def create_candidate_assessor_agent() -> Agent:
    """Create the Candidate Assessor Agent."""
    return Agent(
        role="Senior Candidate Assessor",
        goal="""Provide comprehensive candidate evaluations by synthesizing
        skill matching, experience assessment, and overall fit analysis to
        make hiring recommendations.""",
        backstory="""You are a seasoned hiring manager with experience across
        multiple industries. You've made hundreds of hiring decisions and have
        learned what truly predicts success in a role. You look beyond just
        matching keywords and consider the whole candidate - their potential
        for growth, cultural fit, and long-term value to the organization.""",
        tools=[SkillMatcherTool(), ExperienceMatcherTool()],
        verbose=True,
        allow_delegation=True,
        llm=f"groq/{settings.groq_model}",
    )


def create_ranking_agent() -> Agent:
    """Create the Candidate Ranking Agent."""
    return Agent(
        role="Candidate Ranking Specialist",
        goal="""Rank candidates objectively based on their qualifications
        and fit for the role, providing clear justification for rankings.""",
        backstory="""You are a data-driven recruitment analyst who believes
        in objective, unbiased candidate evaluation. You use structured
        criteria to rank candidates fairly, ensuring that the best candidates
        rise to the top regardless of background. You can justify every ranking
        decision with specific evidence.""",
        tools=[SkillMatcherTool()],
        verbose=True,
        allow_delegation=False,
        llm=f"groq/{settings.groq_model}",
    )

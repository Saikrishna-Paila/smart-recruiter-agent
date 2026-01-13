"""JD Optimization Crew - Analyzes and improves job descriptions."""
from crewai import Crew, Task, Process
from ..agents import create_jd_optimizer_agent, create_jd_analyzer_agent
from ..models.job import Job

def create_jd_optimization_crew():
    """Create the JD Optimization Crew."""
    optimizer = create_jd_optimizer_agent()
    analyzer = create_jd_analyzer_agent()

    return Crew(
        agents=[optimizer, analyzer],
        tasks=[],  # Tasks will be added dynamically
        process=Process.sequential,
        verbose=True,
    )


def run_jd_optimization(job_description: str) -> dict:
    """
    Run JD optimization workflow.

    Args:
        job_description: The job description text to analyze and optimize

    Returns:
        dict with optimized job description
    """
    optimizer = create_jd_optimizer_agent()

    # Single task: Generate optimized job description
    optimize_task = Task(
        description=f"""
        You are a professional job description writer. Take the following job description and create an improved, optimized version.

        IMPORTANT: Your output should ONLY be the new, improved job description text. Do NOT include any analysis, suggestions, or commentary - ONLY output the optimized job description itself.

        Improvements to make:
        1. Improve clarity and readability
        2. Use inclusive, non-biased language
        3. Structure it well with clear sections
        4. Make requirements clear (required vs nice-to-have)
        5. Add compelling company/role value proposition if missing
        6. Optimize for searchability with relevant keywords

        Original Job Description:
        ---
        {job_description}
        ---

        OUTPUT ONLY THE IMPROVED JOB DESCRIPTION TEXT. NO OTHER TEXT.
        """,
        agent=optimizer,
        expected_output="The complete optimized job description text only, no analysis or commentary"
    )

    crew = Crew(
        agents=[optimizer],
        tasks=[optimize_task],
        process=Process.sequential,
        verbose=True,
    )

    result = crew.kickoff()

    return {
        "optimized_description": str(result),
        "status": "completed"
    }


def extract_requirements(job_description: str) -> dict:
    """
    Extract requirements from a job description.

    Args:
        job_description: The job description text

    Returns:
        dict with extracted requirements
    """
    analyzer = create_jd_analyzer_agent()

    extract_task = Task(
        description=f"""
        Extract all requirements from this job description in a structured format.

        For each requirement, identify:
        - The skill/requirement name
        - Whether it's required or nice-to-have
        - The expected proficiency level (entry/intermediate/advanced/expert)

        Job Description:
        {job_description}

        Format your response as a list of requirements.
        """,
        agent=analyzer,
        expected_output="A structured list of job requirements with skill, required status, and level"
    )

    crew = Crew(
        agents=[analyzer],
        tasks=[extract_task],
        process=Process.sequential,
        verbose=True,
    )

    result = crew.kickoff()

    return {
        "requirements": str(result),
        "status": "completed"
    }

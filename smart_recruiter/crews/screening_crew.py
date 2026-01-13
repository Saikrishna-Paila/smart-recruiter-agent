"""Screening Crew - Screens candidates against job requirements."""
import os
import json
from typing import List, Dict, Any, Optional
from crewai import Crew, Task, Process
from ..agents import (
    create_resume_parser_agent,
    create_skill_matcher_agent,
    create_candidate_assessor_agent,
)
from ..tools import ResumeParserTool


def screen_candidate(
    resume_path: str,
    job_requirements: List[Dict],
    job_description: str,
    min_experience_years: int = 0,
    experience_level: str = "mid"
) -> Dict[str, Any]:
    """
    Screen a single candidate against job requirements.

    Args:
        resume_path: Path to the candidate's resume
        job_requirements: List of job requirements
        job_description: The job description text
        min_experience_years: Minimum years of experience required
        experience_level: Expected experience level

    Returns:
        dict with screening results including match score and analysis
    """
    # Verify resume exists
    if not os.path.exists(resume_path):
        return {
            "error": f"Resume not found: {resume_path}",
            "match_score": 0,
            "status": "failed"
        }

    # If no requirements provided, extract key skills from job description
    if not job_requirements:
        # Extract common tech skills mentioned in job description
        common_skills = [
            "python", "javascript", "java", "c++", "go", "rust", "typescript",
            "react", "angular", "vue", "node", "django", "flask", "fastapi",
            "aws", "gcp", "azure", "docker", "kubernetes", "terraform",
            "sql", "postgresql", "mongodb", "redis", "elasticsearch",
            "machine learning", "deep learning", "nlp", "computer vision",
            "pytorch", "tensorflow", "scikit-learn", "pandas", "numpy",
            "api", "rest", "graphql", "microservices", "distributed systems",
            "ci/cd", "git", "agile", "scrum", "leadership", "communication"
        ]
        desc_lower = job_description.lower()
        found_skills = [s for s in common_skills if s in desc_lower]
        job_requirements = [{"skill": s.title(), "level": "intermediate", "required": True} for s in found_skills[:10]]

    parser = create_resume_parser_agent()
    matcher = create_skill_matcher_agent()
    assessor = create_candidate_assessor_agent()

    # Task 1: Parse the resume
    parse_task = Task(
        description=f"""
        Parse the resume at the following path and extract all relevant information:
        - Contact details (name, email, phone)
        - Skills (technical and soft)
        - Work experience (titles, companies, dates, responsibilities)
        - Education (degrees, institutions, dates)
        - Certifications

        Resume path: {resume_path}

        Use the resume_parser tool to read and analyze the resume.
        """,
        agent=parser,
        expected_output="Structured resume data with skills, experience, and education"
    )

    # Task 2: Match skills to requirements
    requirements_json = json.dumps(job_requirements)
    match_task = Task(
        description=f"""
        Using the parsed resume data, match the candidate's skills against job requirements.

        Job Requirements: {requirements_json}

        For EACH requirement listed above:
        1. Check if the candidate has this specific skill/experience
        2. Mark as: MATCH (has it), PARTIAL (related experience), or MISSING (not found)
        3. If MATCH or PARTIAL, cite evidence from the resume

        Be strict - only mark MATCH if the candidate clearly has the skill.
        Related but different skills should be marked as PARTIAL.

        At the end, calculate:
        - Total requirements: X
        - Full matches: Y
        - Partial matches: Z
        - Missing: W
        - Match percentage: (Y + 0.5*Z) / X * 100

        Use the skill_matcher tool with the candidate's skills and job requirements.
        """,
        agent=matcher,
        expected_output="Detailed skill-by-skill match analysis with counts and percentage"
    )

    # Task 3: Overall assessment with strict scoring
    assess_task = Task(
        description=f"""
        Provide a comprehensive assessment of this candidate for the position.

        Job Description:
        {job_description}

        Minimum Experience Required: {min_experience_years} years
        Experience Level: {experience_level}

        SCORING CRITERIA (be strict and objective):
        - 90-100: Perfect match - meets ALL requirements, has relevant experience
        - 75-89: Strong match - meets most requirements (80%+), good experience
        - 60-74: Moderate match - meets some requirements (50-79%), some gaps
        - 40-59: Weak match - meets few requirements (<50%), significant gaps
        - 0-39: Poor match - does not meet key requirements

        IMPORTANT: Be realistic and critical. Most candidates should score between 40-75.
        Only exceptional candidates who match MOST requirements should score above 80.

        For each requirement, check if the candidate actually has that skill/experience.
        Missing required skills should significantly lower the score.

        Your output MUST include this exact format:
        MATCH_SCORE: [number between 0-100]
        RECOMMENDATION: [Strong Hire / Hire / Maybe / No Hire]

        Then provide your detailed analysis.
        """,
        agent=assessor,
        expected_output="Assessment with MATCH_SCORE: XX and RECOMMENDATION: XX followed by analysis"
    )

    crew = Crew(
        agents=[parser, matcher, assessor],
        tasks=[parse_task, match_task, assess_task],
        process=Process.sequential,
        verbose=True,
    )

    try:
        result = crew.kickoff()

        # Try to extract match score from result
        result_str = str(result)
        match_score = extract_score_from_result(result_str)

        return {
            "analysis": result_str,
            "match_score": match_score,
            "status": "completed",
            "recommendation": extract_recommendation(result_str)
        }
    except Exception as e:
        return {
            "error": str(e),
            "match_score": 0,
            "status": "failed"
        }


def screen_multiple_candidates(
    candidates: List[Dict],
    job_requirements: List[Dict],
    job_description: str,
    min_experience_years: int = 0,
    experience_level: str = "mid"
) -> List[Dict[str, Any]]:
    """
    Screen multiple candidates and return ranked results.

    Args:
        candidates: List of candidate dicts with 'id' and 'resume_path'
        job_requirements: List of job requirements
        job_description: The job description text
        min_experience_years: Minimum years required
        experience_level: Expected experience level

    Returns:
        List of screening results, sorted by match score
    """
    results = []

    for candidate in candidates:
        candidate_id = candidate.get('id')
        resume_path = candidate.get('resume_path')

        result = screen_candidate(
            resume_path=resume_path,
            job_requirements=job_requirements,
            job_description=job_description,
            min_experience_years=min_experience_years,
            experience_level=experience_level
        )

        result['candidate_id'] = candidate_id
        results.append(result)

    # Sort by match score, highest first
    results.sort(key=lambda x: x.get('match_score', 0), reverse=True)

    return results


def quick_screen_candidate(
    resume_text: str,
    job_requirements: List[Dict],
    job_description: str,
    min_experience_years: int = 0,
) -> Dict[str, Any]:
    """
    Quick screening using a single agent call (faster than full screening).
    """
    from ..tools import ResumeParserTool

    # If no requirements, extract from job description
    if not job_requirements:
        common_skills = [
            "python", "javascript", "java", "c++", "go", "rust", "typescript",
            "react", "angular", "vue", "node", "django", "flask", "fastapi",
            "aws", "gcp", "azure", "docker", "kubernetes", "machine learning",
            "deep learning", "nlp", "sql", "api", "rest", "microservices"
        ]
        desc_lower = job_description.lower()
        found_skills = [s for s in common_skills if s in desc_lower]
        job_requirements = [{"skill": s.title(), "required": True} for s in found_skills[:10]]

    requirements_list = ", ".join([r.get("skill", "") for r in job_requirements])

    assessor = create_candidate_assessor_agent()

    assess_task = Task(
        description=f"""
        You are screening a candidate. Analyze their resume against the job requirements.

        RESUME TEXT:
        {resume_text[:4000]}

        JOB REQUIREMENTS:
        {requirements_list}

        MINIMUM EXPERIENCE: {min_experience_years} years

        For each requirement, check if the candidate has it:
        - Count MATCHES (clear skill match)
        - Count MISSING (skill not found in resume)

        SCORING RULES:
        - Score = (matches / total_requirements) * 80 + base_20
        - Deduct points for missing REQUIRED skills
        - Most candidates should score 40-70

        OUTPUT FORMAT (required):
        MATCH_SCORE: [0-100]
        RECOMMENDATION: [Strong Hire / Hire / Maybe / No Hire]

        Then list each requirement as MATCH or MISSING with brief explanation.
        """,
        agent=assessor,
        expected_output="MATCH_SCORE and RECOMMENDATION followed by analysis"
    )

    crew = Crew(
        agents=[assessor],
        tasks=[assess_task],
        process=Process.sequential,
        verbose=True,
    )

    try:
        result = crew.kickoff()
        result_str = str(result)
        match_score = extract_score_from_result(result_str)

        return {
            "analysis": result_str,
            "match_score": match_score,
            "status": "completed",
            "recommendation": extract_recommendation(result_str)
        }
    except Exception as e:
        return {
            "error": str(e),
            "match_score": 50,
            "status": "failed"
        }


def extract_score_from_result(result: str) -> int:
    """Extract match score from screening result."""
    import re

    result_lower = result.lower()

    # First, look for our specific MATCH_SCORE format
    match_score_pattern = r'match_score[\s:]*(\d+)'
    match = re.search(match_score_pattern, result_lower)
    if match:
        score = int(match.group(1))
        if 0 <= score <= 100:
            return score

    # Look for other common patterns
    patterns = [
        r'(?:final\s*)?(?:match\s*)?score[\s:]+(\d+)',
        r'(\d+)\s*(?:%|/100|out of 100)',
        r'rating[\s:]+(\d+)',
        r'overall[\s:]+(\d+)',
        r'\*\*(\d+)\*\*\s*(?:%|/100)?',  # **85** or **85%**
    ]

    for pattern in patterns:
        match = re.search(pattern, result_lower)
        if match:
            score = int(match.group(1))
            if 0 <= score <= 100:
                return score

    # Count requirement matches vs misses
    matches = len(re.findall(r'(?:meets|has|matches|qualified|proficient)', result_lower))
    misses = len(re.findall(r'(?:missing|lacks|no experience|not found|does not have|gap)', result_lower))

    if misses > matches:
        base_score = 45
    elif matches > misses * 2:
        base_score = 70
    else:
        base_score = 55

    # Adjust based on recommendation keywords
    if 'strong hire' in result_lower:
        return min(base_score + 20, 90)
    elif 'no hire' in result_lower or 'reject' in result_lower:
        return max(base_score - 20, 25)
    elif 'hire' in result_lower:
        return min(base_score + 10, 80)
    elif 'maybe' in result_lower or 'consider' in result_lower:
        return base_score

    return base_score


def extract_recommendation(result: str) -> str:
    """Extract recommendation from screening result."""
    result_lower = result.lower()

    if 'strong hire' in result_lower:
        return 'strong_hire'
    elif 'strong no hire' in result_lower:
        return 'strong_no_hire'
    elif 'no hire' in result_lower:
        return 'no_hire'
    elif 'hire' in result_lower:
        return 'hire'
    else:
        return 'review'

"""Interview Crew - Prepares interview materials."""
import json
from typing import List, Dict, Any
from crewai import Crew, Task, Process
from ..agents import create_interview_scheduler_agent, create_interview_question_agent


def generate_interview_package(
    job_requirements: List[Dict],
    candidate_skills: List[str],
    job_description: str,
    interview_type: str = "mixed"
) -> Dict[str, Any]:
    """
    Generate a complete interview package for a candidate.

    Args:
        job_requirements: List of job requirements
        candidate_skills: List of candidate's skills
        job_description: The job description text
        interview_type: Type of interview (technical/behavioral/mixed)

    Returns:
        dict with interview questions and scorecard
    """
    scheduler = create_interview_scheduler_agent()
    question_agent = create_interview_question_agent()

    # Task 1: Generate interview questions
    requirements_json = json.dumps(job_requirements)
    skills_json = json.dumps(candidate_skills)

    questions_task = Task(
        description=f"""
        Generate tailored interview questions for this candidate.

        Job Description:
        {job_description}

        Job Requirements: {requirements_json}
        Candidate Skills: {skills_json}
        Interview Type: {interview_type}

        Create questions that:
        1. Assess technical competency in required skills
        2. Identify skill gaps and ability to learn
        3. Evaluate problem-solving approach
        4. Understand past experiences and achievements
        5. Assess cultural fit and soft skills

        Use the interview_question_generator tool with the job requirements and candidate skills.
        """,
        agent=question_agent,
        expected_output="A comprehensive list of interview questions organized by category"
    )

    # Task 2: Create interview scorecard
    scorecard_task = Task(
        description=f"""
        Create a structured interview scorecard for evaluating this candidate.

        Job Requirements: {requirements_json}
        Interview Type: {interview_type}

        The scorecard should include:
        1. Evaluation criteria for each required skill
        2. Rating scale with clear definitions
        3. Space for interviewer notes
        4. Overall recommendation options
        5. Red flags to watch for

        Use the interview_scorecard tool to generate the scorecard.
        """,
        agent=scheduler,
        expected_output="A structured interview scorecard template"
    )

    crew = Crew(
        agents=[question_agent, scheduler],
        tasks=[questions_task, scorecard_task],
        process=Process.sequential,
        verbose=True,
    )

    try:
        result = crew.kickoff()

        return {
            "interview_package": str(result),
            "interview_type": interview_type,
            "status": "completed"
        }
    except Exception as e:
        return {
            "error": str(e),
            "status": "failed"
        }


def generate_technical_questions(
    skills: List[str],
    difficulty: str = "intermediate"
) -> Dict[str, Any]:
    """
    Generate technical interview questions for specific skills.

    Args:
        skills: List of skills to assess
        difficulty: Difficulty level (entry/intermediate/senior)

    Returns:
        dict with technical questions
    """
    question_agent = create_interview_question_agent()

    skills_str = ", ".join(skills)

    tech_task = Task(
        description=f"""
        Generate technical interview questions for the following skills:
        Skills: {skills_str}
        Difficulty Level: {difficulty}

        For each skill, provide:
        1. 2-3 conceptual questions
        2. 1-2 practical/coding questions
        3. 1 system design or architecture question (for senior level)

        Questions should be appropriate for {difficulty} level candidates.
        """,
        agent=question_agent,
        expected_output="Technical interview questions organized by skill"
    )

    crew = Crew(
        agents=[question_agent],
        tasks=[tech_task],
        process=Process.sequential,
        verbose=True,
    )

    try:
        result = crew.kickoff()

        return {
            "questions": str(result),
            "skills": skills,
            "difficulty": difficulty,
            "status": "completed"
        }
    except Exception as e:
        return {
            "error": str(e),
            "status": "failed"
        }


def generate_behavioral_questions(
    competencies: List[str] = None
) -> Dict[str, Any]:
    """
    Generate behavioral interview questions.

    Args:
        competencies: List of competencies to assess (optional)

    Returns:
        dict with behavioral questions
    """
    if not competencies:
        competencies = [
            "leadership",
            "teamwork",
            "problem-solving",
            "communication",
            "adaptability"
        ]

    question_agent = create_interview_question_agent()

    competencies_str = ", ".join(competencies)

    behavioral_task = Task(
        description=f"""
        Generate behavioral interview questions using the STAR method format.

        Competencies to assess: {competencies_str}

        For each competency, provide:
        1. 2-3 behavioral questions starting with "Tell me about a time..."
        2. Follow-up probing questions
        3. What to look for in a good answer

        Questions should reveal how candidates have handled situations in the past.
        """,
        agent=question_agent,
        expected_output="Behavioral interview questions with follow-ups and evaluation criteria"
    )

    crew = Crew(
        agents=[question_agent],
        tasks=[behavioral_task],
        process=Process.sequential,
        verbose=True,
    )

    try:
        result = crew.kickoff()

        return {
            "questions": str(result),
            "competencies": competencies,
            "status": "completed"
        }
    except Exception as e:
        return {
            "error": str(e),
            "status": "failed"
        }

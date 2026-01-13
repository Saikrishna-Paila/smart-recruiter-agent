"""Interview Tools - Generate questions and evaluate responses."""
import json
from typing import List, Dict
from crewai.tools import BaseTool

class InterviewQuestionGeneratorTool(BaseTool):
    """Tool to generate interview questions based on job requirements."""

    name: str = "interview_question_generator"
    description: str = """
    Generates tailored interview questions based on job requirements and candidate profile.
    Input: JSON with 'job_requirements' (list), 'candidate_skills' (list), and 'interview_type' (technical/behavioral/mixed)
    Output: List of relevant interview questions
    """

    def _run(self, input_data: str) -> str:
        """Generate interview questions."""
        try:
            data = json.loads(input_data)
            requirements = data.get('job_requirements', [])
            candidate_skills = data.get('candidate_skills', [])
            interview_type = data.get('interview_type', 'mixed')
        except (json.JSONDecodeError, AttributeError):
            return "Error: Invalid input format. Provide JSON with job_requirements, candidate_skills, and interview_type"

        results = []
        results.append("GENERATED INTERVIEW QUESTIONS")
        results.append("=" * 40)

        # Technical questions based on requirements
        if interview_type in ['technical', 'mixed']:
            results.append("\nTECHNICAL QUESTIONS:")

            tech_questions_templates = {
                'python': [
                    "Explain the difference between lists and tuples in Python.",
                    "How do you handle exceptions in Python?",
                    "What are Python decorators and when would you use them?",
                ],
                'javascript': [
                    "Explain closures in JavaScript and provide an example.",
                    "What is the difference between let, const, and var?",
                    "How does the event loop work in JavaScript?",
                ],
                'react': [
                    "Explain the component lifecycle in React.",
                    "What are React hooks and how do they work?",
                    "How do you optimize performance in a React application?",
                ],
                'sql': [
                    "Explain the difference between INNER JOIN and LEFT JOIN.",
                    "How would you optimize a slow database query?",
                    "What is database normalization and why is it important?",
                ],
                'aws': [
                    "Explain the difference between EC2 and Lambda.",
                    "How would you design a highly available architecture on AWS?",
                    "What is the difference between S3 storage classes?",
                ],
                'docker': [
                    "What is the difference between a Docker image and container?",
                    "How do you optimize Docker images for production?",
                    "Explain Docker networking and how containers communicate.",
                ],
                'default': [
                    "Describe a challenging technical problem you solved recently.",
                    "How do you approach debugging complex issues?",
                    "Walk me through your development workflow.",
                ],
            }

            added_questions = set()
            for req in requirements:
                skill = req.get('skill', '').lower() if isinstance(req, dict) else str(req).lower()
                questions = tech_questions_templates.get(skill, [])
                for q in questions[:2]:
                    if q not in added_questions:
                        results.append(f"  • {q}")
                        added_questions.add(q)

            # Add default questions if few were added
            if len(added_questions) < 3:
                for q in tech_questions_templates['default']:
                    if q not in added_questions:
                        results.append(f"  • {q}")
                        added_questions.add(q)

        # Behavioral questions
        if interview_type in ['behavioral', 'mixed']:
            results.append("\nBEHAVIORAL QUESTIONS:")
            behavioral_questions = [
                "Tell me about a time you had to meet a tight deadline. How did you handle it?",
                "Describe a situation where you had a conflict with a team member. How did you resolve it?",
                "Give an example of when you had to learn a new technology quickly.",
                "Tell me about a project you're most proud of and why.",
                "Describe a time when you received critical feedback. How did you respond?",
                "How do you prioritize tasks when you have multiple deadlines?",
            ]
            for q in behavioral_questions[:4]:
                results.append(f"  • {q}")

        # Skill gap questions
        skill_gaps = []
        candidate_skills_lower = [s.lower() for s in candidate_skills]
        for req in requirements:
            skill = req.get('skill', '').lower() if isinstance(req, dict) else str(req).lower()
            required = req.get('required', True) if isinstance(req, dict) else True
            if required and skill not in candidate_skills_lower:
                skill_gaps.append(skill)

        if skill_gaps:
            results.append("\nSKILL GAP ASSESSMENT QUESTIONS:")
            for skill in skill_gaps[:3]:
                results.append(f"  • How would you approach learning {skill}? What's your plan?")
                results.append(f"  • Do you have any related experience that could help you pick up {skill}?")

        # Closing questions
        results.append("\nCANDIDATE QUESTIONS:")
        results.append("  • What questions do you have about the role or team?")
        results.append("  • What are you looking for in your next position?")

        return "\n".join(results)


class InterviewScorecardTool(BaseTool):
    """Tool to create interview scorecards for structured evaluation."""

    name: str = "interview_scorecard"
    description: str = """
    Creates a structured interview scorecard for evaluating candidates.
    Input: JSON with 'job_requirements', 'evaluation_criteria', and 'interview_type'
    Output: Scorecard template with criteria and rating scale
    """

    def _run(self, input_data: str) -> str:
        """Generate interview scorecard."""
        try:
            data = json.loads(input_data)
            requirements = data.get('job_requirements', [])
            criteria = data.get('evaluation_criteria', [])
            interview_type = data.get('interview_type', 'mixed')
        except (json.JSONDecodeError, AttributeError):
            return "Error: Invalid input format"

        results = []
        results.append("INTERVIEW SCORECARD")
        results.append("=" * 40)
        results.append("\nRATING SCALE: 1-5")
        results.append("  1 = Does not meet requirements")
        results.append("  2 = Partially meets requirements")
        results.append("  3 = Meets requirements")
        results.append("  4 = Exceeds requirements")
        results.append("  5 = Exceptional")

        results.append("\nTECHNICAL SKILLS:")
        for req in requirements[:5]:
            skill = req.get('skill', 'Unknown') if isinstance(req, dict) else str(req)
            results.append(f"  [ ] {skill}: ___ /5")

        results.append("\nCORE COMPETENCIES:")
        competencies = [
            "Problem Solving",
            "Communication",
            "Technical Knowledge",
            "Learning Ability",
            "Team Collaboration",
        ]
        for comp in competencies:
            results.append(f"  [ ] {comp}: ___ /5")

        results.append("\nCULTURAL FIT:")
        cultural = [
            "Alignment with company values",
            "Enthusiasm for the role",
            "Career goals alignment",
        ]
        for c in cultural:
            results.append(f"  [ ] {c}: ___ /5")

        results.append("\nOVERALL ASSESSMENT:")
        results.append("  [ ] Strong Hire")
        results.append("  [ ] Hire")
        results.append("  [ ] No Hire")
        results.append("  [ ] Strong No Hire")

        results.append("\nNOTES:")
        results.append("  Strengths: ________________________________")
        results.append("  Concerns: _________________________________")
        results.append("  Follow-up: ________________________________")

        return "\n".join(results)

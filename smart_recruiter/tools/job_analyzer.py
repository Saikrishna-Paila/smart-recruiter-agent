"""Job Description Analyzer Tool - Analyze and optimize job descriptions."""
import re
from typing import List, Dict
from crewai.tools import BaseTool

class JobDescriptionAnalyzerTool(BaseTool):
    """Tool to analyze job descriptions and extract requirements."""

    name: str = "job_description_analyzer"
    description: str = """
    Analyzes a job description and extracts key requirements, skills, and qualifications.
    Input: Job description text
    Output: Structured analysis with extracted requirements and suggestions
    """

    def _run(self, job_description: str) -> str:
        """Analyze job description and extract requirements."""
        if not job_description or len(job_description.strip()) < 50:
            return "Error: Job description is too short or empty"

        results = []
        results.append("JOB DESCRIPTION ANALYSIS")
        results.append("=" * 40)

        text_lower = job_description.lower()

        # Extract technical skills mentioned
        tech_skills = [
            'python', 'javascript', 'typescript', 'java', 'c++', 'c#', 'go', 'rust', 'ruby', 'php',
            'react', 'angular', 'vue', 'svelte', 'next.js', 'node.js', 'express', 'django', 'flask', 'fastapi', 'spring',
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform', 'ansible',
            'sql', 'postgresql', 'mysql', 'mongodb', 'redis', 'elasticsearch', 'dynamodb',
            'git', 'ci/cd', 'jenkins', 'github actions', 'gitlab',
            'machine learning', 'deep learning', 'tensorflow', 'pytorch', 'nlp', 'computer vision',
            'html', 'css', 'sass', 'tailwind', 'bootstrap',
            'rest api', 'graphql', 'grpc', 'microservices', 'kafka', 'rabbitmq'
        ]

        found_skills = []
        for skill in tech_skills:
            if skill in text_lower:
                found_skills.append(skill)

        results.append(f"\nTECHNICAL SKILLS DETECTED ({len(found_skills)}):")
        if found_skills:
            for skill in found_skills:
                results.append(f"  • {skill}")
        else:
            results.append("  No specific technical skills detected")

        # Extract soft skills
        soft_skills = [
            'communication', 'teamwork', 'leadership', 'problem-solving', 'analytical',
            'creative', 'adaptable', 'organized', 'detail-oriented', 'self-motivated',
            'collaboration', 'mentoring', 'presentation'
        ]

        found_soft_skills = []
        for skill in soft_skills:
            if skill in text_lower:
                found_soft_skills.append(skill)

        if found_soft_skills:
            results.append(f"\nSOFT SKILLS MENTIONED:")
            for skill in found_soft_skills:
                results.append(f"  • {skill}")

        # Extract experience requirements
        exp_patterns = [
            (r'(\d+)\+?\s*years?\s*(?:of\s*)?experience', 'General experience'),
            (r'(\d+)\+?\s*years?\s*(?:of\s*)?(?:professional\s*)?experience', 'Professional experience'),
        ]

        results.append(f"\nEXPERIENCE REQUIREMENTS:")
        found_exp = False
        for pattern, label in exp_patterns:
            match = re.search(pattern, text_lower)
            if match:
                results.append(f"  • {match.group(1)}+ years required")
                found_exp = True
                break
        if not found_exp:
            results.append("  • Not explicitly specified")

        # Check for education requirements
        education_keywords = ['bachelor', 'master', 'phd', 'degree', 'bs', 'ms', 'mba', 'computer science', 'engineering']
        found_education = []
        for kw in education_keywords:
            if kw in text_lower:
                found_education.append(kw)

        results.append(f"\nEDUCATION REQUIREMENTS:")
        if found_education:
            results.append(f"  • Keywords found: {', '.join(found_education)}")
        else:
            results.append("  • Not explicitly specified")

        # Check for remote/location
        results.append(f"\nWORK ARRANGEMENT:")
        if 'remote' in text_lower:
            results.append("  • Remote work mentioned")
        if 'hybrid' in text_lower:
            results.append("  • Hybrid work mentioned")
        if 'on-site' in text_lower or 'onsite' in text_lower:
            results.append("  • On-site work mentioned")

        # Job level detection
        results.append(f"\nJOB LEVEL:")
        if 'senior' in text_lower or 'sr.' in text_lower:
            results.append("  • Senior level")
        elif 'lead' in text_lower or 'principal' in text_lower:
            results.append("  • Lead/Principal level")
        elif 'junior' in text_lower or 'jr.' in text_lower or 'entry' in text_lower:
            results.append("  • Junior/Entry level")
        else:
            results.append("  • Mid-level (assumed)")

        # Word count
        word_count = len(job_description.split())
        results.append(f"\nDESCRIPTION STATS:")
        results.append(f"  • Word count: {word_count}")
        if word_count < 100:
            results.append("  • ⚠ Description may be too brief")
        elif word_count > 1000:
            results.append("  • ⚠ Description may be too long")
        else:
            results.append("  • ✓ Good length")

        return "\n".join(results)


class JobOptimizationTool(BaseTool):
    """Tool to suggest improvements for job descriptions."""

    name: str = "job_optimization"
    description: str = """
    Analyzes a job description and provides optimization suggestions for better candidate attraction.
    Input: Job description text
    Output: Optimization suggestions and recommendations
    """

    def _run(self, job_description: str) -> str:
        """Provide optimization suggestions for job description."""
        if not job_description:
            return "Error: No job description provided"

        results = []
        results.append("JOB DESCRIPTION OPTIMIZATION SUGGESTIONS")
        results.append("=" * 40)

        text_lower = job_description.lower()
        suggestions = []

        # Check for inclusive language
        exclusive_terms = ['rockstar', 'ninja', 'guru', 'wizard', 'young', 'energetic']
        found_exclusive = [t for t in exclusive_terms if t in text_lower]
        if found_exclusive:
            suggestions.append(f"Remove potentially exclusive terms: {', '.join(found_exclusive)}")

        # Check for benefits
        benefit_keywords = ['benefits', 'vacation', 'pto', '401k', 'health', 'insurance', 'equity', 'bonus']
        found_benefits = [b for b in benefit_keywords if b in text_lower]
        if not found_benefits:
            suggestions.append("Consider adding information about benefits and perks")

        # Check for salary
        if 'salary' not in text_lower and '$' not in job_description and 'compensation' not in text_lower:
            suggestions.append("Consider adding salary range for transparency")

        # Check for company culture
        culture_keywords = ['culture', 'values', 'mission', 'team', 'environment']
        found_culture = [c for c in culture_keywords if c in text_lower]
        if len(found_culture) < 2:
            suggestions.append("Add more details about company culture and team environment")

        # Check for growth opportunities
        growth_keywords = ['growth', 'career', 'learning', 'development', 'training', 'mentor']
        found_growth = [g for g in growth_keywords if g in text_lower]
        if not found_growth:
            suggestions.append("Highlight growth and learning opportunities")

        # Check for clear responsibilities
        if 'responsibilities' not in text_lower and 'duties' not in text_lower and 'you will' not in text_lower:
            suggestions.append("Clearly outline job responsibilities and day-to-day duties")

        # Format suggestions
        if suggestions:
            results.append("\nRECOMMENDATIONS:")
            for i, suggestion in enumerate(suggestions, 1):
                results.append(f"  {i}. {suggestion}")
        else:
            results.append("\n✓ Job description looks well-optimized!")

        # General best practices
        results.append("\nBEST PRACTICES CHECKLIST:")
        checks = [
            ("Clear job title", 'title' in text_lower or len(job_description.split('\n')[0]) < 100),
            ("Responsibilities listed", 'responsibilities' in text_lower or 'you will' in text_lower),
            ("Requirements specified", 'requirements' in text_lower or 'qualifications' in text_lower),
            ("Benefits mentioned", any(b in text_lower for b in benefit_keywords)),
            ("Contact information", 'apply' in text_lower or 'contact' in text_lower),
        ]

        for check_name, passed in checks:
            status = "✓" if passed else "✗"
            results.append(f"  {status} {check_name}")

        return "\n".join(results)

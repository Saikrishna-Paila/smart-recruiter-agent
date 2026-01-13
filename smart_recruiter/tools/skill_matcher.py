"""Skill Matcher Tool - Match candidate skills against job requirements."""
from typing import List, Dict, Any
from crewai.tools import BaseTool
from pydantic import Field

class SkillMatcherTool(BaseTool):
    """Tool to match candidate skills against job requirements."""

    name: str = "skill_matcher"
    description: str = """
    Compares candidate skills against job requirements and calculates a match score.
    Input: JSON string with 'candidate_skills' (list of skills) and 'job_requirements' (list of required skills)
    Output: Match analysis with score and skill gaps
    """

    def _run(self, input_data: str) -> str:
        """Match candidate skills against job requirements."""
        import json

        try:
            data = json.loads(input_data)
            candidate_skills = [s.lower().strip() for s in data.get('candidate_skills', [])]
            job_requirements = data.get('job_requirements', [])
        except (json.JSONDecodeError, AttributeError):
            return "Error: Invalid input format. Please provide JSON with 'candidate_skills' and 'job_requirements'"

        if not job_requirements:
            return "Error: No job requirements provided"

        results = []
        matched_required = []
        missing_required = []
        matched_optional = []
        missing_optional = []

        for req in job_requirements:
            skill = req.get('skill', '').lower().strip()
            required = req.get('required', True)
            level = req.get('level', 'intermediate')

            # Check if skill is present (with fuzzy matching)
            is_matched = False
            for cs in candidate_skills:
                if skill in cs or cs in skill:
                    is_matched = True
                    break

            if is_matched:
                if required:
                    matched_required.append(skill)
                else:
                    matched_optional.append(skill)
            else:
                if required:
                    missing_required.append(skill)
                else:
                    missing_optional.append(skill)

        # Calculate score
        total_required = len(matched_required) + len(missing_required)
        total_optional = len(matched_optional) + len(missing_optional)

        required_score = (len(matched_required) / total_required * 100) if total_required > 0 else 100
        optional_score = (len(matched_optional) / total_optional * 100) if total_optional > 0 else 100

        # Weighted average: required skills worth more
        overall_score = (required_score * 0.7 + optional_score * 0.3)

        results.append(f"SKILL MATCH ANALYSIS")
        results.append(f"=" * 40)
        results.append(f"\nOVERALL MATCH SCORE: {overall_score:.1f}%")
        results.append(f"Required Skills Score: {required_score:.1f}%")
        results.append(f"Optional Skills Score: {optional_score:.1f}%")

        results.append(f"\nMATCHED REQUIRED SKILLS ({len(matched_required)}/{total_required}):")
        for skill in matched_required:
            results.append(f"  ✓ {skill}")

        if missing_required:
            results.append(f"\nMISSING REQUIRED SKILLS ({len(missing_required)}):")
            for skill in missing_required:
                results.append(f"  ✗ {skill}")

        if matched_optional:
            results.append(f"\nMATCHED OPTIONAL SKILLS ({len(matched_optional)}/{total_optional}):")
            for skill in matched_optional:
                results.append(f"  ✓ {skill}")

        if missing_optional:
            results.append(f"\nMISSING OPTIONAL SKILLS ({len(missing_optional)}):")
            for skill in missing_optional:
                results.append(f"  ○ {skill}")

        # Recommendation
        results.append(f"\nRECOMMENDATION:")
        if overall_score >= 80:
            results.append("  Strong candidate - recommend for interview")
        elif overall_score >= 60:
            results.append("  Good candidate with some skill gaps - consider for interview")
        elif overall_score >= 40:
            results.append("  Moderate match - may need significant training")
        else:
            results.append("  Low match - consider other candidates")

        return "\n".join(results)


class ExperienceMatcherTool(BaseTool):
    """Tool to evaluate candidate experience against job requirements."""

    name: str = "experience_matcher"
    description: str = """
    Evaluates candidate's work experience against job requirements.
    Input: JSON with 'candidate_experiences' (list of experience entries) and 'min_years' (required years), 'experience_level'
    Output: Experience analysis and fit assessment
    """

    def _run(self, input_data: str) -> str:
        """Evaluate candidate experience."""
        import json
        from datetime import datetime

        try:
            data = json.loads(input_data)
            experiences = data.get('candidate_experiences', [])
            min_years = data.get('min_years', 0)
            exp_level = data.get('experience_level', 'mid')
        except (json.JSONDecodeError, AttributeError):
            return "Error: Invalid input format"

        results = []
        results.append("EXPERIENCE ANALYSIS")
        results.append("=" * 40)

        # Calculate total years
        total_years = 0
        for exp in experiences:
            start = exp.get('start_date', '')
            end = exp.get('end_date', 'Present')

            try:
                if isinstance(start, str) and start:
                    start_year = int(start.split('-')[0]) if '-' in start else int(start)
                else:
                    continue

                if end.lower() == 'present' or not end:
                    end_year = datetime.now().year
                else:
                    end_year = int(end.split('-')[0]) if '-' in end else int(end)

                total_years += (end_year - start_year)
            except (ValueError, AttributeError):
                continue

        results.append(f"\nTotal Experience: ~{total_years} years")
        results.append(f"Required: {min_years}+ years ({exp_level} level)")

        # Experience level mapping
        level_years = {
            'entry': (0, 2),
            'mid': (2, 5),
            'senior': (5, 10),
            'lead': (8, 15),
        }

        expected_range = level_years.get(exp_level, (0, 100))

        results.append(f"\nEVALUATION:")
        if total_years >= min_years:
            results.append(f"  ✓ Meets minimum experience requirement")
        else:
            results.append(f"  ✗ Below minimum experience requirement (gap: {min_years - total_years} years)")

        if expected_range[0] <= total_years <= expected_range[1]:
            results.append(f"  ✓ Experience aligns with {exp_level} level")
        elif total_years > expected_range[1]:
            results.append(f"  ⚠ May be overqualified for {exp_level} level")
        else:
            results.append(f"  ⚠ May be underqualified for {exp_level} level")

        # List experience entries
        if experiences:
            results.append(f"\nWORK HISTORY:")
            for exp in experiences[:5]:
                title = exp.get('title', 'Unknown')
                company = exp.get('company', 'Unknown')
                results.append(f"  • {title} at {company}")

        return "\n".join(results)

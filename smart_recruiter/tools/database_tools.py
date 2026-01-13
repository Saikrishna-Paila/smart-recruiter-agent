"""Database Tools - Interface for database operations in CrewAI."""
import json
from typing import Optional
from crewai.tools import BaseTool

class GetJobTool(BaseTool):
    """Tool to retrieve job details from the database."""

    name: str = "get_job"
    description: str = """
    Retrieves job details from the database.
    Input: job_id (string)
    Output: Job details as JSON
    """

    def _run(self, job_id: str) -> str:
        """Get job details (placeholder - actual implementation will use database)."""
        # This will be called with actual database in the crew context
        return f"Job details for {job_id} - Use actual database session in crew context"


class GetCandidateTool(BaseTool):
    """Tool to retrieve candidate details."""

    name: str = "get_candidate"
    description: str = """
    Retrieves candidate details from the database.
    Input: candidate_id (string)
    Output: Candidate details as JSON
    """

    def _run(self, candidate_id: str) -> str:
        """Get candidate details."""
        return f"Candidate details for {candidate_id} - Use actual database session in crew context"


class UpdateCandidateScoreTool(BaseTool):
    """Tool to update candidate match score."""

    name: str = "update_candidate_score"
    description: str = """
    Updates candidate's match score and screening notes.
    Input: JSON with 'candidate_id', 'match_score' (0-100), and 'notes'
    Output: Confirmation of update
    """

    def _run(self, input_data: str) -> str:
        """Update candidate score."""
        try:
            data = json.loads(input_data)
            candidate_id = data.get('candidate_id')
            score = data.get('match_score')
            notes = data.get('notes', '')
            return f"Updated candidate {candidate_id} with score {score} - Use actual database in crew context"
        except json.JSONDecodeError:
            return "Error: Invalid JSON input"


class ListCandidatesForJobTool(BaseTool):
    """Tool to list all candidates for a job."""

    name: str = "list_candidates_for_job"
    description: str = """
    Lists all candidates who applied for a specific job.
    Input: job_id (string)
    Output: List of candidates with basic info
    """

    def _run(self, job_id: str) -> str:
        """List candidates for job."""
        return f"Candidates for job {job_id} - Use actual database session in crew context"

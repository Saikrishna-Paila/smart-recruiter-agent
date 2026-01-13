"""
Smart Recruiter Data Models
===========================

Pydantic models for structured data.
"""

from .candidate import (
    Candidate,
    CandidateCreate,
    CandidateUpdate,
    CandidateStatus,
    Skill,
    SkillLevel,
    Experience,
    Education,
)
from .job import (
    Job,
    JobCreate,
    JobUpdate,
    JobStatus,
    JobType,
    ExperienceLevel,
    Requirement,
    SalaryRange,
)
from .result import (
    MatchResult,
    SkillMatch,
    ScreeningResult,
    InterviewSchedule,
    InterviewKit,
    InterviewQuestion,
    InterviewType,
    InterviewStatus,
)

__all__ = [
    # Candidate
    "Candidate",
    "CandidateCreate",
    "CandidateUpdate",
    "CandidateStatus",
    "Skill",
    "SkillLevel",
    "Experience",
    "Education",
    # Job
    "Job",
    "JobCreate",
    "JobUpdate",
    "JobStatus",
    "JobType",
    "ExperienceLevel",
    "Requirement",
    "SalaryRange",
    # Results
    "MatchResult",
    "SkillMatch",
    "ScreeningResult",
    "InterviewSchedule",
    "InterviewKit",
    "InterviewQuestion",
    "InterviewType",
    "InterviewStatus",
]

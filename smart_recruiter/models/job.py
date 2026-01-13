"""
Job Data Models
===============

Models for job postings and requirements.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum
import uuid


class JobStatus(str, Enum):
    """Status of a job posting."""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    CLOSED = "closed"
    FILLED = "filled"


class JobType(str, Enum):
    """Type of employment."""
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    INTERNSHIP = "internship"
    FREELANCE = "freelance"


class ExperienceLevel(str, Enum):
    """Required experience level."""
    ENTRY = "entry"
    MID = "mid"
    SENIOR = "senior"
    LEAD = "lead"
    EXECUTIVE = "executive"


class Requirement(BaseModel):
    """A skill or requirement for the job."""
    skill: str
    level: str = "intermediate"  # beginner, intermediate, advanced, expert
    required: bool = True  # True = required, False = nice-to-have
    weight: float = 1.0  # Importance weight for scoring


class SalaryRange(BaseModel):
    """Salary range for the position."""
    min_salary: Optional[int] = None
    max_salary: Optional[int] = None
    currency: str = "USD"
    period: str = "yearly"  # yearly, monthly, hourly


class Job(BaseModel):
    """
    Complete job posting.
    Created by recruiter, optimized by JD Agent.
    """
    # Identifiers
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])

    # Basic Info
    title: str
    department: Optional[str] = None
    location: Optional[str] = None
    remote_option: bool = False
    job_type: JobType = JobType.FULL_TIME
    experience_level: ExperienceLevel = ExperienceLevel.MID

    # Description
    description: str  # Original description
    optimized_description: Optional[str] = None  # After JD Optimizer
    responsibilities: List[str] = Field(default_factory=list)
    benefits: List[str] = Field(default_factory=list)

    # Requirements
    requirements: List[Requirement] = Field(default_factory=list)
    min_experience_years: float = 0.0
    education_required: Optional[str] = None

    # Compensation
    salary: Optional[SalaryRange] = None

    # Application Settings
    application_deadline: Optional[datetime] = None
    max_applicants: Optional[int] = None

    # Status
    status: JobStatus = JobStatus.DRAFT

    # Statistics
    total_applicants: int = 0
    screened_count: int = 0
    shortlisted_count: int = 0
    interviewed_count: int = 0

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    published_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None

    # Hired candidate (when filled)
    hired_candidate_id: Optional[str] = None

    @property
    def required_skills(self) -> List[str]:
        """Get list of required skill names."""
        return [r.skill for r in self.requirements if r.required]

    @property
    def nice_to_have_skills(self) -> List[str]:
        """Get list of nice-to-have skill names."""
        return [r.skill for r in self.requirements if not r.required]

    @property
    def all_skills(self) -> List[str]:
        """Get all skill names."""
        return [r.skill for r in self.requirements]

    @property
    def is_active(self) -> bool:
        """Check if job is accepting applications."""
        return self.status == JobStatus.ACTIVE

    @property
    def application_link(self) -> str:
        """Generate application link for candidates."""
        return f"/apply/{self.id}"

    def add_requirement(self, skill: str, required: bool = True, level: str = "intermediate"):
        """Add a skill requirement."""
        self.requirements.append(Requirement(
            skill=skill,
            required=required,
            level=level
        ))

    class Config:
        json_schema_extra = {
            "example": {
                "id": "job_001",
                "title": "Senior Python Developer",
                "department": "Engineering",
                "location": "San Francisco, CA",
                "remote_option": True,
                "job_type": "full_time",
                "experience_level": "senior",
                "description": "We are looking for a Senior Python Developer...",
                "requirements": [
                    {"skill": "Python", "level": "expert", "required": True},
                    {"skill": "SQL", "level": "advanced", "required": True},
                    {"skill": "AWS", "level": "intermediate", "required": True},
                    {"skill": "Kubernetes", "level": "intermediate", "required": False},
                ],
                "min_experience_years": 5,
                "salary": {
                    "min_salary": 150000,
                    "max_salary": 200000,
                    "currency": "USD"
                },
                "status": "active",
                "total_applicants": 234,
            }
        }


class JobCreate(BaseModel):
    """Data required to create a new job."""
    title: str
    description: str
    department: Optional[str] = None
    location: Optional[str] = None
    remote_option: bool = False
    job_type: JobType = JobType.FULL_TIME
    experience_level: ExperienceLevel = ExperienceLevel.MID
    requirements: List[Requirement] = Field(default_factory=list)
    min_experience_years: float = 0.0
    salary: Optional[SalaryRange] = None


class JobUpdate(BaseModel):
    """Fields that can be updated."""
    title: Optional[str] = None
    description: Optional[str] = None
    optimized_description: Optional[str] = None
    status: Optional[JobStatus] = None
    requirements: Optional[List[Requirement]] = None

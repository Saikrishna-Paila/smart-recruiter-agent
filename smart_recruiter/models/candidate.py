"""
Candidate Data Models
=====================

Models for candidate information extracted from resumes.
"""

from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from datetime import date, datetime
from enum import Enum


class CandidateStatus(str, Enum):
    """Status of a candidate in the pipeline."""
    APPLIED = "applied"
    SCREENING = "screening"
    SHORTLISTED = "shortlisted"
    INTERVIEW = "interview"
    OFFERED = "offered"
    HIRED = "hired"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


class SkillLevel(str, Enum):
    """Skill proficiency level."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class Skill(BaseModel):
    """A skill with proficiency level."""
    name: str
    level: SkillLevel = SkillLevel.INTERMEDIATE
    years: Optional[float] = None

    def __str__(self):
        return f"{self.name} ({self.level.value})"


class Experience(BaseModel):
    """Work experience entry."""
    company: str
    title: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None  # None = current
    description: Optional[str] = None
    achievements: List[str] = Field(default_factory=list)
    is_current: bool = False

    @property
    def duration_years(self) -> float:
        """Calculate duration in years."""
        end = self.end_date or date.today()
        start = self.start_date or end
        days = (end - start).days
        return round(days / 365.25, 1)


class Education(BaseModel):
    """Education entry."""
    institution: str
    degree: str
    field_of_study: Optional[str] = None
    graduation_year: Optional[int] = None
    gpa: Optional[float] = None


class Candidate(BaseModel):
    """
    Complete candidate profile extracted from resume.
    This is what the Resume Parser Agent produces.
    """
    # Basic Info
    id: Optional[str] = None
    job_id: Optional[str] = None
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None

    # Professional Summary
    summary: Optional[str] = None

    # Skills
    skills: List[Skill] = Field(default_factory=list)

    # Experience
    experiences: List[Experience] = Field(default_factory=list)

    # Education
    education: List[Education] = Field(default_factory=list)

    # Calculated Fields
    total_experience_years: float = 0.0

    # Resume File
    resume_path: Optional[str] = None
    resume_text: Optional[str] = None

    # Status & Scoring
    status: CandidateStatus = CandidateStatus.APPLIED
    match_score: Optional[float] = None
    ai_assessment: Optional[str] = None

    # Timestamps
    applied_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @property
    def skill_names(self) -> List[str]:
        """Get list of skill names."""
        return [s.name for s in self.skills]

    @property
    def latest_company(self) -> Optional[str]:
        """Get most recent company."""
        if self.experiences:
            return self.experiences[0].company
        return None

    @property
    def latest_title(self) -> Optional[str]:
        """Get most recent job title."""
        if self.experiences:
            return self.experiences[0].title
        return None

    def calculate_total_experience(self) -> float:
        """Calculate total years of experience."""
        total = sum(exp.duration_years for exp in self.experiences)
        self.total_experience_years = round(total, 1)
        return self.total_experience_years

    class Config:
        json_schema_extra = {
            "example": {
                "name": "John Doe",
                "email": "john.doe@email.com",
                "phone": "+1-555-123-4567",
                "location": "San Francisco, CA",
                "skills": [
                    {"name": "Python", "level": "expert", "years": 5},
                    {"name": "SQL", "level": "advanced", "years": 4},
                ],
                "experiences": [
                    {
                        "company": "TechCorp",
                        "title": "Senior Software Engineer",
                        "start_date": "2021-01-01",
                        "is_current": True,
                    }
                ],
                "education": [
                    {
                        "institution": "Stanford University",
                        "degree": "BS",
                        "field_of_study": "Computer Science",
                        "graduation_year": 2017,
                    }
                ],
                "total_experience_years": 6.5,
                "match_score": 87.5,
            }
        }


class CandidateCreate(BaseModel):
    """Data required when candidate applies via form."""
    name: str
    email: EmailStr
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    cover_letter: Optional[str] = None
    # Resume file is uploaded separately


class CandidateUpdate(BaseModel):
    """Fields that can be updated."""
    status: Optional[CandidateStatus] = None
    match_score: Optional[float] = None
    ai_assessment: Optional[str] = None

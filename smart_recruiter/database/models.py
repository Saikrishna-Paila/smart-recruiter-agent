"""
SQLAlchemy Database Models
==========================

Database tables for persistent storage.
"""

from sqlalchemy import (
    Column, String, Integer, Float, Boolean, Text, DateTime, JSON, ForeignKey, Enum
)
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from .connection import Base


def generate_uuid():
    return str(uuid.uuid4())[:8]


class JobDB(Base):
    """Jobs table."""
    __tablename__ = "jobs"

    id = Column(String(8), primary_key=True, default=generate_uuid)
    title = Column(String(255), nullable=False)
    department = Column(String(100))
    location = Column(String(255))
    remote_option = Column(Boolean, default=False)
    job_type = Column(String(50), default="full_time")
    experience_level = Column(String(50), default="mid")

    # Description
    description = Column(Text, nullable=False)
    optimized_description = Column(Text)
    responsibilities = Column(JSON, default=list)
    benefits = Column(JSON, default=list)

    # Requirements stored as JSON
    requirements = Column(JSON, default=list)
    min_experience_years = Column(Float, default=0.0)
    education_required = Column(String(255))

    # Salary
    salary_min = Column(Integer)
    salary_max = Column(Integer)
    salary_currency = Column(String(10), default="USD")

    # Status
    status = Column(String(50), default="draft")

    # Stats
    total_applicants = Column(Integer, default=0)
    screened_count = Column(Integer, default=0)
    shortlisted_count = Column(Integer, default=0)
    interviewed_count = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(DateTime)
    closed_at = Column(DateTime)

    # Relationships
    candidates = relationship("CandidateDB", back_populates="job", cascade="all, delete-orphan")
    interviews = relationship("InterviewDB", back_populates="job", cascade="all, delete-orphan")


class CandidateDB(Base):
    """Candidates table."""
    __tablename__ = "candidates"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    job_id = Column(String(8), ForeignKey("jobs.id"), nullable=False)

    # Basic Info
    name = Column(String(255), nullable=False)
    email = Column(String(255))
    phone = Column(String(50))
    location = Column(String(255))
    linkedin_url = Column(String(500))
    github_url = Column(String(500))
    portfolio_url = Column(String(500))

    # Professional
    summary = Column(Text)
    skills = Column(JSON, default=list)  # List of skill objects
    experiences = Column(JSON, default=list)  # List of experience objects
    education = Column(JSON, default=list)  # List of education objects
    total_experience_years = Column(Float, default=0.0)

    # Resume
    resume_path = Column(String(500))
    resume_text = Column(Text)

    # Cover letter (from application form)
    cover_letter = Column(Text)

    # Status & Scoring
    status = Column(String(50), default="applied")
    match_score = Column(Float)
    ai_assessment = Column(Text)

    # Match details stored as JSON
    match_details = Column(JSON)

    # Timestamps
    applied_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    screened_at = Column(DateTime)
    interviewed_at = Column(DateTime)

    # Relationships
    job = relationship("JobDB", back_populates="candidates")
    interviews = relationship("InterviewDB", back_populates="candidate", cascade="all, delete-orphan")


class InterviewDB(Base):
    """Interviews table."""
    __tablename__ = "interviews"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    candidate_id = Column(String(36), ForeignKey("candidates.id"), nullable=False)
    job_id = Column(String(8), ForeignKey("jobs.id"), nullable=False)

    # Interview Details
    interview_type = Column(String(50), default="technical")
    scheduled_at = Column(DateTime, nullable=False)
    duration_minutes = Column(Integer, default=60)

    # Participants
    interviewer_name = Column(String(255))
    interviewer_email = Column(String(255))

    # Location
    is_remote = Column(Boolean, default=True)
    meeting_link = Column(String(500))
    location = Column(String(255))

    # Status
    status = Column(String(50), default="scheduled")

    # Communication
    invite_sent = Column(Boolean, default=False)
    reminder_sent = Column(Boolean, default=False)

    # Feedback
    feedback = Column(Text)
    rating = Column(Integer)

    # Interview kit (generated questions)
    interview_kit = Column(JSON)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime)

    # Relationships
    candidate = relationship("CandidateDB", back_populates="interviews")
    job = relationship("JobDB", back_populates="interviews")

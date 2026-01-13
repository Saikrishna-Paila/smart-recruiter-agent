"""
Application Routes
==================

Public endpoints for candidates to apply to jobs.
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from datetime import datetime
import os
import uuid
import aiofiles

from ...database import get_db, CandidateDB, JobDB
from ...config import get_settings

settings = get_settings()
router = APIRouter()


@router.get("/{job_id}", response_model=dict)
async def get_job_for_application(job_id: str, db: AsyncSession = Depends(get_db)):
    """Get public job details for application page."""
    result = await db.execute(select(JobDB).where(JobDB.id == job_id))
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.status != "active":
        raise HTTPException(status_code=400, detail="This job is not accepting applications")

    return {
        "id": job.id,
        "title": job.title,
        "department": job.department,
        "location": job.location,
        "remote_option": job.remote_option,
        "job_type": job.job_type,
        "description": job.optimized_description or job.description,
        "responsibilities": job.responsibilities or [],
        "benefits": job.benefits or [],
        "requirements": [
            {
                "skill": r.get("skill"),
                "level": r.get("level"),
                "required": r.get("required", True),
            }
            for r in (job.requirements or [])
        ],
        "min_experience_years": job.min_experience_years,
        "salary": {
            "min": job.salary_min,
            "max": job.salary_max,
            "currency": job.salary_currency,
        } if job.salary_min or job.salary_max else None,
    }


@router.post("/{job_id}", response_model=dict)
async def submit_application(
    job_id: str,
    name: str = Form(...),
    email: str = Form(...),
    phone: Optional[str] = Form(None),
    linkedin_url: Optional[str] = Form(None),
    github_url: Optional[str] = Form(None),
    portfolio_url: Optional[str] = Form(None),
    cover_letter: Optional[str] = Form(None),
    resume: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Submit job application with resume.
    This is the PUBLIC endpoint for candidates.
    """
    # Verify job exists and is active
    job_result = await db.execute(select(JobDB).where(JobDB.id == job_id))
    job = job_result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.status != "active":
        raise HTTPException(status_code=400, detail="This job is not accepting applications")

    # Check if already applied with same email
    existing = await db.execute(
        select(CandidateDB).where(
            CandidateDB.job_id == job_id,
            CandidateDB.email == email
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="You have already applied for this position")

    # Validate file type
    allowed_extensions = [".pdf", ".docx", ".doc"]
    file_ext = os.path.splitext(resume.filename)[1].lower()
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
        )

    # Check file size
    content = await resume.read()
    if len(content) > settings.max_file_size_mb * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {settings.max_file_size_mb}MB"
        )

    # Reset file position
    await resume.seek(0)

    # Create candidate ID
    candidate_id = str(uuid.uuid4())[:8]

    # Save resume file
    job_resume_dir = os.path.join(settings.resume_dir, job_id)
    os.makedirs(job_resume_dir, exist_ok=True)

    safe_name = "".join(c for c in name if c.isalnum() or c in " -_").strip()[:50]
    filename = f"{candidate_id}_{safe_name}{file_ext}"
    filepath = os.path.join(job_resume_dir, filename)

    async with aiofiles.open(filepath, "wb") as f:
        await f.write(content)

    # Create candidate record
    candidate = CandidateDB(
        id=candidate_id,
        job_id=job_id,
        name=name,
        email=email,
        phone=phone,
        linkedin_url=linkedin_url,
        github_url=github_url,
        portfolio_url=portfolio_url,
        cover_letter=cover_letter,
        resume_path=filepath,
        status="applied",
        applied_at=datetime.utcnow(),
    )

    db.add(candidate)

    # Update job applicant count
    job.total_applicants += 1
    job.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(candidate)

    return {
        "success": True,
        "candidate_id": candidate.id,
        "message": f"Thank you for applying, {name}! We will review your application and get back to you soon.",
        "applied_at": candidate.applied_at.isoformat(),
    }


@router.get("/{job_id}/check/{email}", response_model=dict)
async def check_application_status(
    job_id: str,
    email: str,
    db: AsyncSession = Depends(get_db)
):
    """Check application status by email."""
    result = await db.execute(
        select(CandidateDB).where(
            CandidateDB.job_id == job_id,
            CandidateDB.email == email
        )
    )
    candidate = result.scalar_one_or_none()

    if not candidate:
        raise HTTPException(status_code=404, detail="Application not found")

    status_messages = {
        "applied": "Your application has been received and is being reviewed.",
        "screening": "Your application is currently being screened.",
        "shortlisted": "Congratulations! You have been shortlisted for this position.",
        "interview": "You have been selected for an interview.",
        "offered": "An offer has been extended to you.",
        "hired": "Congratulations! You have been hired.",
        "rejected": "Thank you for your interest. Unfortunately, we have decided to move forward with other candidates.",
    }

    return {
        "status": candidate.status,
        "message": status_messages.get(candidate.status, "Application in progress"),
        "applied_at": candidate.applied_at.isoformat() if candidate.applied_at else None,
        "match_score": candidate.match_score,
    }

"""
Jobs API Routes
===============

CRUD operations for job postings.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from datetime import datetime

from ...database import get_db, JobDB, CandidateDB
from ...models import Job, JobCreate, JobUpdate, JobStatus

router = APIRouter()


@router.get("/", response_model=List[dict])
async def list_jobs(
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Get all jobs with optional status filter."""
    query = select(JobDB)

    if status:
        query = query.where(JobDB.status == status)

    query = query.offset(skip).limit(limit).order_by(JobDB.created_at.desc())
    result = await db.execute(query)
    jobs = result.scalars().all()

    return [
        {
            "id": job.id,
            "title": job.title,
            "department": job.department,
            "location": job.location,
            "status": job.status,
            "total_applicants": job.total_applicants,
            "screened_count": job.screened_count,
            "shortlisted_count": job.shortlisted_count,
            "created_at": job.created_at.isoformat() if job.created_at else None,
        }
        for job in jobs
    ]


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_job(
    job_data: JobCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new job posting."""
    job = JobDB(
        title=job_data.title,
        description=job_data.description,
        department=job_data.department,
        location=job_data.location,
        remote_option=job_data.remote_option,
        job_type=job_data.job_type.value,
        experience_level=job_data.experience_level.value,
        requirements=[r.model_dump() for r in job_data.requirements],
        min_experience_years=job_data.min_experience_years,
        salary_min=job_data.salary.min_salary if job_data.salary else None,
        salary_max=job_data.salary.max_salary if job_data.salary else None,
        status="draft",
    )

    db.add(job)
    await db.commit()
    await db.refresh(job)

    return {
        "id": job.id,
        "title": job.title,
        "status": job.status,
        "message": "Job created successfully",
        "application_link": f"/apply/{job.id}",
    }


@router.get("/{job_id}", response_model=dict)
async def get_job(job_id: str, db: AsyncSession = Depends(get_db)):
    """Get job details by ID."""
    result = await db.execute(select(JobDB).where(JobDB.id == job_id))
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return {
        "id": job.id,
        "title": job.title,
        "department": job.department,
        "location": job.location,
        "remote_option": job.remote_option,
        "job_type": job.job_type,
        "experience_level": job.experience_level,
        "description": job.description,
        "optimized_description": job.optimized_description,
        "responsibilities": job.responsibilities or [],
        "benefits": job.benefits or [],
        "requirements": job.requirements or [],
        "min_experience_years": job.min_experience_years,
        "salary": {
            "min": job.salary_min,
            "max": job.salary_max,
            "currency": job.salary_currency,
        } if job.salary_min or job.salary_max else None,
        "status": job.status,
        "total_applicants": job.total_applicants,
        "screened_count": job.screened_count,
        "shortlisted_count": job.shortlisted_count,
        "interviewed_count": job.interviewed_count,
        "created_at": job.created_at.isoformat() if job.created_at else None,
        "published_at": job.published_at.isoformat() if job.published_at else None,
        "application_link": f"/apply/{job.id}",
    }


@router.put("/{job_id}", response_model=dict)
async def update_job(
    job_id: str,
    job_data: JobUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a job posting."""
    result = await db.execute(select(JobDB).where(JobDB.id == job_id))
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Update fields
    if job_data.title is not None:
        job.title = job_data.title
    if job_data.description is not None:
        job.description = job_data.description
    if job_data.optimized_description is not None:
        job.optimized_description = job_data.optimized_description
    if job_data.status is not None:
        job.status = job_data.status.value
        if job_data.status == JobStatus.ACTIVE and not job.published_at:
            job.published_at = datetime.utcnow()
        elif job_data.status == JobStatus.CLOSED:
            job.closed_at = datetime.utcnow()
    if job_data.requirements is not None:
        job.requirements = [r.model_dump() for r in job_data.requirements]

    job.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(job)

    return {
        "id": job.id,
        "status": job.status,
        "message": "Job updated successfully",
    }


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job(job_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a job posting."""
    result = await db.execute(select(JobDB).where(JobDB.id == job_id))
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    await db.delete(job)
    await db.commit()


@router.patch("/{job_id}/status", response_model=dict)
async def update_job_status(
    job_id: str,
    data: dict,
    db: AsyncSession = Depends(get_db)
):
    """Update job status (active, paused, closed, etc.)."""
    result = await db.execute(select(JobDB).where(JobDB.id == job_id))
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    new_status = data.get("status")
    if new_status:
        job.status = new_status
        if new_status == "active" and not job.published_at:
            job.published_at = datetime.utcnow()
        job.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(job)

    return {
        "id": job.id,
        "status": job.status,
        "message": f"Job status updated to {job.status}",
    }


@router.post("/{job_id}/publish", response_model=dict)
async def publish_job(job_id: str, db: AsyncSession = Depends(get_db)):
    """Publish a job (change status to active)."""
    result = await db.execute(select(JobDB).where(JobDB.id == job_id))
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    job.status = "active"
    job.published_at = datetime.utcnow()
    job.updated_at = datetime.utcnow()

    await db.commit()

    return {
        "id": job.id,
        "status": job.status,
        "published_at": job.published_at.isoformat(),
        "application_link": f"/apply/{job.id}",
        "message": "Job published successfully",
    }


@router.get("/{job_id}/stats", response_model=dict)
async def get_job_stats(job_id: str, db: AsyncSession = Depends(get_db)):
    """Get statistics for a job."""
    result = await db.execute(select(JobDB).where(JobDB.id == job_id))
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Get candidate counts by status
    status_query = select(
        CandidateDB.status,
        func.count(CandidateDB.id)
    ).where(
        CandidateDB.job_id == job_id
    ).group_by(CandidateDB.status)

    status_result = await db.execute(status_query)
    status_counts = dict(status_result.all())

    # Get average score
    avg_query = select(func.avg(CandidateDB.match_score)).where(
        CandidateDB.job_id == job_id,
        CandidateDB.match_score.isnot(None)
    )
    avg_result = await db.execute(avg_query)
    avg_score = avg_result.scalar()

    return {
        "job_id": job_id,
        "total_applicants": job.total_applicants,
        "by_status": status_counts,
        "average_match_score": round(avg_score, 1) if avg_score else None,
        "screened_count": job.screened_count,
        "shortlisted_count": job.shortlisted_count,
        "interviewed_count": job.interviewed_count,
    }

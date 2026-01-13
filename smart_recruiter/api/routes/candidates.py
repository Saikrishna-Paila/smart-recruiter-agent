"""
Candidates API Routes
=====================

CRUD operations for candidates.
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from datetime import datetime
import os
import uuid

from ...database import get_db, CandidateDB, JobDB
from ...models import CandidateStatus, CandidateUpdate
from ...config import get_settings
from ...services import send_screening_result, send_interview_invite
from sqlalchemy import func

settings = get_settings()
router = APIRouter()


async def recalculate_job_counts(db: AsyncSession, job_id: str):
    """Recalculate job counts from actual candidate data."""
    job_result = await db.execute(select(JobDB).where(JobDB.id == job_id))
    job = job_result.scalar_one_or_none()
    if not job:
        return

    # Count total applicants
    total_query = await db.execute(
        select(func.count()).select_from(CandidateDB).where(CandidateDB.job_id == job_id)
    )
    job.total_applicants = total_query.scalar() or 0

    # Count screened (those with match_score)
    screened_query = await db.execute(
        select(func.count()).select_from(CandidateDB).where(
            CandidateDB.job_id == job_id,
            CandidateDB.match_score.isnot(None)
        )
    )
    job.screened_count = screened_query.scalar() or 0

    # Count shortlisted
    shortlisted_query = await db.execute(
        select(func.count()).select_from(CandidateDB).where(
            CandidateDB.job_id == job_id,
            CandidateDB.status == 'shortlisted'
        )
    )
    job.shortlisted_count = shortlisted_query.scalar() or 0

    # Count interviewed
    interviewed_query = await db.execute(
        select(func.count()).select_from(CandidateDB).where(
            CandidateDB.job_id == job_id,
            CandidateDB.status.in_(['interview_scheduled', 'hired'])
        )
    )
    job.interviewed_count = interviewed_query.scalar() or 0


@router.get("/job/{job_id}", response_model=List[dict])
async def list_candidates_for_job(
    job_id: str,
    status: Optional[str] = None,
    min_score: Optional[float] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Get all candidates for a specific job."""
    # Verify job exists
    job_result = await db.execute(select(JobDB).where(JobDB.id == job_id))
    if not job_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Job not found")

    query = select(CandidateDB).where(CandidateDB.job_id == job_id)

    if status:
        query = query.where(CandidateDB.status == status)

    if min_score is not None:
        query = query.where(CandidateDB.match_score >= min_score)

    # Order by score (highest first), then by applied date
    query = query.order_by(
        CandidateDB.match_score.desc().nullslast(),
        CandidateDB.applied_at.desc()
    ).offset(skip).limit(limit)

    result = await db.execute(query)
    candidates = result.scalars().all()

    return [
        {
            "id": c.id,
            "name": c.name,
            "email": c.email,
            "status": c.status,
            "match_score": c.match_score,
            "total_experience_years": c.total_experience_years,
            "skills": [s.get("name") if isinstance(s, dict) else s for s in (c.skills or [])[:5]],
            "latest_company": c.experiences[0].get("company") if c.experiences else None,
            "latest_title": c.experiences[0].get("title") if c.experiences else None,
            "applied_at": c.applied_at.isoformat() if c.applied_at else None,
        }
        for c in candidates
    ]


@router.get("/{candidate_id}", response_model=dict)
async def get_candidate(candidate_id: str, db: AsyncSession = Depends(get_db)):
    """Get candidate details by ID."""
    result = await db.execute(select(CandidateDB).where(CandidateDB.id == candidate_id))
    candidate = result.scalar_one_or_none()

    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    return {
        "id": candidate.id,
        "job_id": candidate.job_id,
        "name": candidate.name,
        "email": candidate.email,
        "phone": candidate.phone,
        "location": candidate.location,
        "linkedin_url": candidate.linkedin_url,
        "github_url": candidate.github_url,
        "portfolio_url": candidate.portfolio_url,
        "summary": candidate.summary,
        "skills": candidate.skills or [],
        "experiences": candidate.experiences or [],
        "education": candidate.education or [],
        "total_experience_years": candidate.total_experience_years,
        "resume_path": candidate.resume_path,
        "cover_letter": candidate.cover_letter,
        "status": candidate.status,
        "match_score": candidate.match_score,
        "match_details": candidate.match_details,
        "ai_assessment": candidate.ai_assessment,
        "applied_at": candidate.applied_at.isoformat() if candidate.applied_at else None,
        "screened_at": candidate.screened_at.isoformat() if candidate.screened_at else None,
    }


@router.put("/{candidate_id}", response_model=dict)
async def update_candidate(
    candidate_id: str,
    update_data: CandidateUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update candidate status or details."""
    result = await db.execute(select(CandidateDB).where(CandidateDB.id == candidate_id))
    candidate = result.scalar_one_or_none()

    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    if update_data.status is not None:
        candidate.status = update_data.status.value
        if update_data.status == CandidateStatus.INTERVIEW:
            candidate.interviewed_at = datetime.utcnow()

    if update_data.match_score is not None:
        candidate.match_score = update_data.match_score

    if update_data.ai_assessment is not None:
        candidate.ai_assessment = update_data.ai_assessment

    candidate.updated_at = datetime.utcnow()

    # Recalculate job counts from actual data
    await recalculate_job_counts(db, candidate.job_id)

    await db.commit()
    await db.refresh(candidate)

    return {
        "id": candidate.id,
        "status": candidate.status,
        "message": "Candidate updated successfully",
    }


@router.delete("/{candidate_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_candidate(candidate_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a candidate."""
    result = await db.execute(select(CandidateDB).where(CandidateDB.id == candidate_id))
    candidate = result.scalar_one_or_none()

    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    job_id = candidate.job_id

    # Delete resume file if exists
    if candidate.resume_path and os.path.exists(candidate.resume_path):
        os.remove(candidate.resume_path)

    await db.delete(candidate)

    # Recalculate job counts after deletion
    await recalculate_job_counts(db, job_id)
    await db.commit()


@router.patch("/{candidate_id}/status", response_model=dict)
async def update_candidate_status(
    candidate_id: str,
    data: dict,
    db: AsyncSession = Depends(get_db)
):
    """Update candidate status."""
    result = await db.execute(select(CandidateDB).where(CandidateDB.id == candidate_id))
    candidate = result.scalar_one_or_none()

    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    new_status = data.get("status")
    if new_status:
        candidate.status = new_status
        candidate.updated_at = datetime.utcnow()

        # Recalculate job counts from actual data
        await recalculate_job_counts(db, candidate.job_id)

    await db.commit()
    await db.refresh(candidate)

    return {
        "id": candidate.id,
        "status": candidate.status,
        "message": f"Candidate status updated to {candidate.status}",
    }


@router.get("/{candidate_id}/resume")
async def get_candidate_resume(candidate_id: str, db: AsyncSession = Depends(get_db)):
    """Download candidate's resume file."""
    result = await db.execute(select(CandidateDB).where(CandidateDB.id == candidate_id))
    candidate = result.scalar_one_or_none()

    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    if not candidate.resume_path:
        raise HTTPException(status_code=404, detail="Resume not found")

    if not os.path.exists(candidate.resume_path):
        raise HTTPException(status_code=404, detail="Resume file not found on server")

    # Get filename from path
    filename = os.path.basename(candidate.resume_path)

    return FileResponse(
        path=candidate.resume_path,
        filename=filename,
        media_type="application/octet-stream"
    )


@router.post("/{candidate_id}/shortlist", response_model=dict)
async def shortlist_candidate(candidate_id: str, db: AsyncSession = Depends(get_db)):
    """Move candidate to shortlist."""
    result = await db.execute(select(CandidateDB).where(CandidateDB.id == candidate_id))
    candidate = result.scalar_one_or_none()

    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    candidate.status = "shortlisted"
    candidate.updated_at = datetime.utcnow()

    # Recalculate job counts
    await recalculate_job_counts(db, candidate.job_id)
    await db.commit()

    return {
        "id": candidate.id,
        "status": candidate.status,
        "message": "Candidate shortlisted",
    }


@router.post("/{candidate_id}/reject", response_model=dict)
async def reject_candidate(candidate_id: str, db: AsyncSession = Depends(get_db)):
    """Reject a candidate."""
    result = await db.execute(select(CandidateDB).where(CandidateDB.id == candidate_id))
    candidate = result.scalar_one_or_none()

    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    candidate.status = "rejected"
    candidate.updated_at = datetime.utcnow()

    # Recalculate job counts (in case moving from shortlisted)
    await recalculate_job_counts(db, candidate.job_id)
    await db.commit()

    return {
        "id": candidate.id,
        "status": candidate.status,
        "message": "Candidate rejected",
    }


@router.post("/{candidate_id}/send-assessment", response_model=dict)
async def send_assessment_email(candidate_id: str, db: AsyncSession = Depends(get_db)):
    """Send AI assessment result email to candidate."""
    result = await db.execute(select(CandidateDB).where(CandidateDB.id == candidate_id))
    candidate = result.scalar_one_or_none()

    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    # Get job details
    job_result = await db.execute(select(JobDB).where(JobDB.id == candidate.job_id))
    job = job_result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Check if candidate has been screened
    if candidate.match_score is None:
        raise HTTPException(status_code=400, detail="Candidate has not been screened yet")

    # Send email
    email_result = send_screening_result(
        candidate_email=candidate.email,
        candidate_name=candidate.name,
        job_title=job.title,
        match_score=candidate.match_score,
        status=candidate.status,
        assessment_summary=candidate.ai_assessment,
    )

    if email_result.get("success"):
        return {
            "id": candidate.id,
            "email": candidate.email,
            "message": "Assessment email sent successfully",
            "email_id": email_result.get("email_id"),
        }
    elif email_result.get("preview"):
        # Resend is in test mode - return preview instead of error
        return {
            "id": candidate.id,
            "email": candidate.email,
            "message": "Email preview generated (Resend in test mode)",
            "test_mode": True,
            "preview": email_result.get("preview"),
            "note": "To send real emails, verify a domain at resend.com/domains",
        }
    else:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to send email: {email_result.get('error')}"
        )


@router.post("/{candidate_id}/send-interview-invite", response_model=dict)
async def send_interview_invitation(
    candidate_id: str,
    interview_date: Optional[str] = None,
    interview_link: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Send interview invitation email to candidate."""
    result = await db.execute(select(CandidateDB).where(CandidateDB.id == candidate_id))
    candidate = result.scalar_one_or_none()

    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    # Get job details
    job_result = await db.execute(select(JobDB).where(JobDB.id == candidate.job_id))
    job = job_result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Send interview invite email
    email_result = send_interview_invite(
        candidate_email=candidate.email,
        candidate_name=candidate.name,
        job_title=job.title,
        interview_date=interview_date,
        interview_link=interview_link,
    )

    if email_result.get("success"):
        # Update candidate status to interview_scheduled
        candidate.status = "interview_scheduled"
        candidate.updated_at = datetime.utcnow()
        await db.commit()

        return {
            "id": candidate.id,
            "email": candidate.email,
            "message": "Interview invitation sent successfully",
            "email_id": email_result.get("email_id"),
        }
    elif email_result.get("preview"):
        # Resend is in test mode - still update status but note it's a preview
        candidate.status = "interview_scheduled"
        candidate.updated_at = datetime.utcnow()
        await db.commit()

        return {
            "id": candidate.id,
            "email": candidate.email,
            "message": "Interview invite preview generated (Resend in test mode)",
            "test_mode": True,
            "preview": email_result.get("preview"),
            "note": "Status updated. To send real emails, verify a domain at resend.com/domains",
        }
    else:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to send email: {email_result.get('error')}"
        )

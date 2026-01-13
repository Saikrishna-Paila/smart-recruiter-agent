"""
Screening API Routes
====================

Endpoints for triggering AI screening and matching.
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from datetime import datetime
import asyncio
import json

from ...database import get_db, JobDB, CandidateDB
from ...config import get_settings

settings = get_settings()
router = APIRouter()


async def run_screening_task(
    job_id: str,
    candidates_data: list,
    job_requirements: list,
    job_description: str,
    min_exp: int,
    exp_level: str,
):
    """
    Background task to run AI screening.
    This imports crews here to avoid import issues at startup.
    """
    from ...crews import screen_candidate
    from ...database import async_session

    async with async_session() as db:
        for candidate in candidates_data:
            try:
                # Run the screening crew
                result = screen_candidate(
                    resume_path=candidate['resume_path'],
                    job_requirements=job_requirements,
                    job_description=job_description,
                    min_experience_years=min_exp,
                    experience_level=exp_level,
                )

                # Update candidate with results
                candidate_query = await db.execute(
                    select(CandidateDB).where(CandidateDB.id == candidate['id'])
                )
                candidate_db = candidate_query.scalar_one_or_none()

                if candidate_db:
                    candidate_db.match_score = result.get('match_score', 0)
                    candidate_db.screening_notes = result.get('analysis', '')
                    candidate_db.status = 'screening'
                    candidate_db.screened_at = datetime.utcnow()

                    # Set status based on score
                    if result.get('match_score', 0) >= settings.min_match_score:
                        candidate_db.status = 'shortlisted'
                    else:
                        candidate_db.status = 'rejected'

                    await db.commit()

            except Exception as e:
                print(f"Error screening candidate {candidate['id']}: {e}")
                continue

        # Update job counts
        job_query = await db.execute(select(JobDB).where(JobDB.id == job_id))
        job = job_query.scalar_one_or_none()
        if job:
            # Recalculate counts
            screened = await db.execute(
                select(CandidateDB).where(
                    CandidateDB.job_id == job_id,
                    CandidateDB.match_score.isnot(None)
                )
            )
            job.screened_count = len(screened.scalars().all())

            shortlisted = await db.execute(
                select(CandidateDB).where(
                    CandidateDB.job_id == job_id,
                    CandidateDB.status == 'shortlisted'
                )
            )
            job.shortlisted_count = len(shortlisted.scalars().all())
            await db.commit()


@router.post("/job/{job_id}/screen", response_model=dict)
async def screen_candidates(
    job_id: str,
    background_tasks: BackgroundTasks,
    limit: Optional[int] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Trigger AI screening for all unscreened candidates in a job.
    This runs the Resume Parser → Skill Matcher agents.
    """
    # Verify job exists
    job_result = await db.execute(select(JobDB).where(JobDB.id == job_id))
    job = job_result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Get unscreened candidates
    query = select(CandidateDB).where(
        CandidateDB.job_id == job_id,
        CandidateDB.status == "applied",
        CandidateDB.match_score.is_(None)
    )

    if limit:
        query = query.limit(limit)

    result = await db.execute(query)
    candidates = result.scalars().all()

    if not candidates:
        return {
            "job_id": job_id,
            "message": "No unscreened candidates found",
            "screened_count": 0,
        }

    # Prepare data for background task
    candidates_data = [
        {
            "id": c.id,
            "resume_path": c.resume_path,
        }
        for c in candidates
        if c.resume_path
    ]

    job_requirements = job.requirements or []
    job_description = job.description or ""

    # Add background task for screening
    background_tasks.add_task(
        run_screening_task,
        job_id,
        candidates_data,
        job_requirements,
        job_description,
        job.min_experience_years or 0,
        job.experience_level or "mid",
    )

    return {
        "job_id": job_id,
        "message": f"Screening initiated for {len(candidates_data)} candidates",
        "candidates_to_screen": len(candidates_data),
        "status": "processing",
        "note": "CrewAI agents are processing candidates in the background",
    }


@router.post("/job/{job_id}/optimize-jd", response_model=dict)
async def optimize_job_description(
    job_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Trigger JD Optimizer Agent to improve job description.
    Returns the optimized description for user to review before applying.
    """
    from ...crews import run_jd_optimization

    # Verify job exists
    job_result = await db.execute(select(JobDB).where(JobDB.id == job_id))
    job = job_result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Always run optimization (user can re-run to get new suggestions)
    try:
        result = run_jd_optimization(job.description or "")

        # Return optimized description for user review (don't save yet)
        return {
            "job_id": job_id,
            "message": "JD optimization completed",
            "optimized_description": result.get("optimized_description", ""),
            "original_description": job.description,
            "status": "completed",
        }
    except Exception as e:
        return {
            "job_id": job_id,
            "message": f"JD optimization failed: {str(e)}",
            "status": "failed",
        }


@router.post("/candidate/{candidate_id}/generate-questions", response_model=dict)
async def generate_interview_questions(
    candidate_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Trigger Assessment Agent to generate interview questions for a candidate.
    """
    from ...crews import generate_interview_package

    # Verify candidate exists
    result = await db.execute(select(CandidateDB).where(CandidateDB.id == candidate_id))
    candidate = result.scalar_one_or_none()

    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    # Get job details
    job_result = await db.execute(select(JobDB).where(JobDB.id == candidate.job_id))
    job = job_result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Generate interview questions
    try:
        candidate_skills = [
            s.get("name") if isinstance(s, dict) else str(s)
            for s in (candidate.skills or [])
        ]

        result = generate_interview_package(
            job_requirements=job.requirements or [],
            candidate_skills=candidate_skills,
            job_description=job.description or "",
            interview_type="mixed",
        )

        return {
            "candidate_id": candidate_id,
            "candidate_name": candidate.name,
            "job_title": job.title,
            "interview_package": result.get("interview_package", ""),
            "status": result.get("status", "completed"),
        }
    except Exception as e:
        return {
            "candidate_id": candidate_id,
            "candidate_name": candidate.name,
            "message": f"Question generation failed: {str(e)}",
            "status": "failed",
        }


@router.post("/candidate/{candidate_id}/rescreen", response_model=dict)
async def rescreen_candidate(
    candidate_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Re-screen a specific candidate with AI agents (fast mode)."""
    from ...crews import quick_screen_candidate
    from ...tools import ResumeParserTool, ResumeAnalyzerTool

    # Get candidate
    result = await db.execute(select(CandidateDB).where(CandidateDB.id == candidate_id))
    candidate = result.scalar_one_or_none()

    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    # Get job
    job_result = await db.execute(select(JobDB).where(JobDB.id == candidate.job_id))
    job = job_result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if not candidate.resume_path:
        raise HTTPException(status_code=400, detail="No resume found for candidate")

    # Parse resume to extract skills
    parser = ResumeParserTool()
    analyzer = ResumeAnalyzerTool()

    try:
        # Parse resume
        resume_text = parser._run(candidate.resume_path)
        analysis = analyzer._run(resume_text)

        # Extract skills from analysis
        extracted_skills = []
        if "DETECTED SKILLS:" in analysis:
            skills_line = [line for line in analysis.split('\n') if 'DETECTED SKILLS:' in line]
            if skills_line:
                skills_str = skills_line[0].split('DETECTED SKILLS:')[1].strip()
                extracted_skills = [{"name": s.strip(), "level": "intermediate"} for s in skills_str.split(',')]

        # Run quick screening (single agent, faster)
        screening_result = quick_screen_candidate(
            resume_text=resume_text,
            job_requirements=job.requirements or [],
            job_description=job.description or "",
            min_experience_years=job.min_experience_years or 0,
        )

        # Update candidate
        candidate.skills = extracted_skills
        candidate.match_score = screening_result.get('match_score', 0)
        candidate.ai_assessment = screening_result.get('analysis', '')
        candidate.match_details = {
            "recommendation": screening_result.get('recommendation', 'review'),
            "resume_analysis": analysis[:1000],
        }
        candidate.screened_at = datetime.utcnow()

        # Update status based on score
        if candidate.match_score >= settings.min_match_score:
            candidate.status = 'shortlisted'
        else:
            candidate.status = 'rejected'

        await db.commit()
        await db.refresh(candidate)

        return {
            "candidate_id": candidate_id,
            "match_score": candidate.match_score,
            "skills_extracted": len(extracted_skills),
            "skills": extracted_skills,
            "status": candidate.status,
            "recommendation": screening_result.get('recommendation', 'review'),
            "message": "Candidate re-screened successfully"
        }

    except Exception as e:
        return {
            "candidate_id": candidate_id,
            "message": f"Re-screening failed: {str(e)}",
            "status": "failed"
        }


@router.get("/job/{job_id}/results", response_model=dict)
async def get_screening_results(
    job_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get screening results and statistics for a job.
    """
    # Verify job exists
    job_result = await db.execute(select(JobDB).where(JobDB.id == job_id))
    job = job_result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Get screened candidates (those with match scores)
    screened_query = select(CandidateDB).where(
        CandidateDB.job_id == job_id,
        CandidateDB.match_score.isnot(None)
    ).order_by(CandidateDB.match_score.desc())

    result = await db.execute(screened_query)
    screened_candidates = result.scalars().all()

    # Calculate statistics
    scores = [c.match_score for c in screened_candidates if c.match_score]
    avg_score = sum(scores) / len(scores) if scores else 0

    # Score distribution
    distribution = {
        "90-100": len([s for s in scores if 90 <= s <= 100]),
        "80-89": len([s for s in scores if 80 <= s < 90]),
        "70-79": len([s for s in scores if 70 <= s < 80]),
        "60-69": len([s for s in scores if 60 <= s < 70]),
        "below_60": len([s for s in scores if s < 60]),
    }

    # Top candidates
    top_candidates = [
        {
            "id": c.id,
            "name": c.name,
            "score": c.match_score,
            "status": c.status,
        }
        for c in screened_candidates[:10]
    ]

    return {
        "job_id": job_id,
        "job_title": job.title,
        "total_applicants": job.total_applicants,
        "screened_count": len(screened_candidates),
        "average_score": round(avg_score, 1),
        "score_distribution": distribution,
        "top_candidates": top_candidates,
        "qualified_count": len([s for s in scores if s >= settings.min_match_score]),
    }

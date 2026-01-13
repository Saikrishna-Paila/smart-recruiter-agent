"""Email Service - Send emails to candidates using Resend."""
import resend
from typing import Optional
from ..config import settings


def init_resend():
    """Initialize Resend with API key."""
    if settings.resend_api_key:
        resend.api_key = settings.resend_api_key
        return True
    return False


def send_screening_result(
    candidate_email: str,
    candidate_name: str,
    job_title: str,
    match_score: float,
    status: str,
    assessment_summary: Optional[str] = None,
) -> dict:
    """
    Send screening result email to candidate.

    Args:
        candidate_email: Candidate's email address
        candidate_name: Candidate's name
        job_title: Job title they applied for
        match_score: Their match score (0-100)
        status: Current status (shortlisted, rejected, etc.)
        assessment_summary: Optional AI assessment summary

    Returns:
        dict with send status
    """
    if not init_resend():
        return {"success": False, "error": "Email service not configured"}

    # Determine email content based on status
    if status == "shortlisted":
        subject = f"Great News! You've Been Shortlisted for {job_title}"
        status_message = "Congratulations! After careful review of your application, we're pleased to inform you that you've been shortlisted for the next stage of our hiring process."
        next_steps = "Our team will be in touch shortly to schedule an interview. Please ensure your contact information is up to date."
    elif status == "rejected":
        subject = f"Update on Your Application for {job_title}"
        status_message = "Thank you for your interest in this position. After careful consideration, we've decided to move forward with other candidates whose qualifications more closely match our current needs."
        next_steps = "We encourage you to apply for future positions that match your skills and experience. We wish you the best in your job search."
    else:
        subject = f"Application Update: {job_title}"
        status_message = "Thank you for applying. Your application is currently under review."
        next_steps = "We'll be in touch with updates on your application status."

    # Build email HTML
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #0284c7, #0369a1); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f9fafb; padding: 30px; border-radius: 0 0 10px 10px; }}
            .score-box {{ background: white; padding: 20px; border-radius: 10px; text-align: center; margin: 20px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            .score {{ font-size: 48px; font-weight: bold; color: {'#22c55e' if match_score >= 70 else '#eab308' if match_score >= 50 else '#ef4444'}; }}
            .assessment {{ background: white; padding: 20px; border-radius: 10px; margin: 20px 0; border-left: 4px solid #0284c7; }}
            .footer {{ text-align: center; padding: 20px; color: #6b7280; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Smart Recruiter</h1>
                <p>AI-Powered Recruitment Platform</p>
            </div>
            <div class="content">
                <h2>Hello {candidate_name},</h2>
                <p>{status_message}</p>

                <div class="score-box">
                    <p style="margin: 0; color: #6b7280;">Your Match Score</p>
                    <div class="score">{match_score:.0f}%</div>
                    <p style="margin: 0; color: #6b7280;">for {job_title}</p>
                </div>

                {f'<div class="assessment"><h3>AI Assessment Summary</h3><p>{assessment_summary[:500]}...</p></div>' if assessment_summary else ''}

                <h3>Next Steps</h3>
                <p>{next_steps}</p>

                <p>Best regards,<br>The Recruitment Team</p>
            </div>
            <div class="footer">
                <p>This email was sent by Smart Recruiter AI</p>
                <p>Project 4 of 12 AI Projects 2026</p>
            </div>
        </div>
    </body>
    </html>
    """

    try:
        params = {
            "from": settings.email_from,
            "to": [candidate_email],
            "subject": subject,
            "html": html_content,
        }

        response = resend.Emails.send(params)
        return {"success": True, "email_id": response.get("id"), "message": "Email sent successfully"}
    except Exception as e:
        error_msg = str(e)
        # Handle Resend test mode limitation
        if "testing emails to your own email" in error_msg or "verify a domain" in error_msg:
            return {
                "success": False,
                "error": "Resend is in test mode. Emails can only be sent to your registered email. To send to candidates, verify a domain at resend.com/domains",
                "preview": {
                    "to": candidate_email,
                    "subject": subject,
                    "status": status,
                    "score": match_score
                }
            }
        return {"success": False, "error": error_msg}


def send_interview_invite(
    candidate_email: str,
    candidate_name: str,
    job_title: str,
    interview_date: Optional[str] = None,
    interview_link: Optional[str] = None,
    questions_preview: Optional[str] = None,
) -> dict:
    """
    Send interview invitation email to candidate.
    """
    if not init_resend():
        return {"success": False, "error": "Email service not configured"}

    subject = f"Interview Invitation: {job_title}"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #0284c7, #0369a1); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f9fafb; padding: 30px; border-radius: 0 0 10px 10px; }}
            .highlight {{ background: #dbeafe; padding: 20px; border-radius: 10px; margin: 20px 0; }}
            .button {{ display: inline-block; background: #0284c7; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 10px 0; }}
            .footer {{ text-align: center; padding: 20px; color: #6b7280; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Interview Invitation</h1>
                <p>{job_title}</p>
            </div>
            <div class="content">
                <h2>Hello {candidate_name},</h2>
                <p>Congratulations! We were impressed with your application and would like to invite you for an interview.</p>

                <div class="highlight">
                    <h3>Interview Details</h3>
                    {f'<p><strong>Date:</strong> {interview_date}</p>' if interview_date else '<p>Our team will contact you to schedule a convenient time.</p>'}
                    {f'<p><a href="{interview_link}" class="button">Join Interview</a></p>' if interview_link else ''}
                </div>

                {f'<h3>Topics to Prepare</h3><p>{questions_preview}</p>' if questions_preview else ''}

                <h3>Tips for Success</h3>
                <ul>
                    <li>Review the job description and your application</li>
                    <li>Prepare examples of relevant projects and experiences</li>
                    <li>Have questions ready about the role and company</li>
                    <li>Test your equipment if it's a video interview</li>
                </ul>

                <p>We look forward to speaking with you!</p>

                <p>Best regards,<br>The Recruitment Team</p>
            </div>
            <div class="footer">
                <p>Smart Recruiter AI - Project 4 of 12 AI Projects 2026</p>
            </div>
        </div>
    </body>
    </html>
    """

    try:
        params = {
            "from": settings.email_from,
            "to": [candidate_email],
            "subject": subject,
            "html": html_content,
        }

        response = resend.Emails.send(params)
        return {"success": True, "email_id": response.get("id"), "message": "Interview invite sent"}
    except Exception as e:
        error_msg = str(e)
        # Handle Resend test mode limitation
        if "testing emails to your own email" in error_msg or "verify a domain" in error_msg:
            return {
                "success": False,
                "error": "Resend is in test mode. Emails can only be sent to your registered email. To send to candidates, verify a domain at resend.com/domains",
                "preview": {
                    "to": candidate_email,
                    "subject": subject,
                    "interview_date": interview_date,
                    "interview_link": interview_link
                }
            }
        return {"success": False, "error": error_msg}

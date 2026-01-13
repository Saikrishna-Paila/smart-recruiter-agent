"""Smart Recruiter Services."""
from .email_service import send_screening_result, send_interview_invite

__all__ = [
    'send_screening_result',
    'send_interview_invite',
]

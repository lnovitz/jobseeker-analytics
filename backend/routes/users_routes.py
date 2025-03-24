import logging
from fastapi import APIRouter, Depends, Request
from sqlmodel import Session, select
from db.user_emails import UserEmails
from utils.config_utils import get_settings
from session.session_layer import validate_session
from database import engine

# Logger setup
logger = logging.getLogger(__name__)

# Get settings
settings = get_settings()
APP_URL = settings.APP_URL

api_call_finished = False

# FastAPI router for email routes
router = APIRouter()


@router.get("/user-response-rate")
def calculate_response_rate(
    request: Request, user_id: str = Depends(validate_session)
) -> None:
    with Session(engine) as session:
        user_emails = session.exec(
            select(UserEmails).where(UserEmails.user_id == user_id)
        ).all()

        # if user has no application just return 0.0
        total_apps = len(user_emails)
        if total_apps == 0:
            return 0.0

        interview_requests = 0
        for email in user_emails:
            # using request for avalability as an interview request as it should come before the offer and shecduled interview
            if (
                email.application_status
                and email.application_status.lower() == "request for availability"
            ):
                interview_requests += 1

        response_rate_percent = (interview_requests / total_apps) * 100
        return round(response_rate_percent, 1)

import logging
from typing import List
from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from sqlmodel import Session, select, desc
from googleapiclient.discovery import build
from constants import QUERY_APPLIED_EMAIL_FILTER
from db.user_emails import UserEmails
from db.utils.user_email_utils import create_user_email
from utils.auth_utils import AuthenticatedUser
from utils.email_utils import get_email_ids, get_email
from utils.llm_utils import process_email
from utils.config_utils import get_settings
from session.session_layer import validate_session
from database import engine

# Logger setup
logger = logging.getLogger(__name__)

# Get settings
settings = get_settings()
APP_URL = settings.APP_URL

api_call_finished = False
total_emails = 0
processed_emails = 0

# FastAPI router for email routes
router = APIRouter()

@router.get("/processing", response_class=HTMLResponse)
async def processing(request: Request, user_id: str = Depends(validate_session)):
    logging.info("user_id:%s processing", user_id)
    global api_call_finished, total_emails, processed_emails
    if not user_id:
        logger.info("user_id: not found, redirecting to login")
        return RedirectResponse("/logout", status_code=303)
    if api_call_finished:
        logger.info("user_id: %s processing complete", user_id)
        return JSONResponse(
            content={
                "message": "Processing complete",
                "processed_emails": processed_emails,
                "total_emails": total_emails,
            }
        )
    else:
        logger.info("user_id: %s processing not complete for file", user_id)
        return JSONResponse(
            content={
                    "message": "Processing in progress",
                    "processed_emails": processed_emails,
                    "total_emails": total_emails
                }
            )
    

@router.get("/get-emails", response_model=List[UserEmails])
def query_emails(request: Request, user_id: str = Depends(validate_session)) -> None:
    with Session(engine) as session:
        try:
            logger.info(f"Fetching emails for user_id: {user_id}")

            # Query emails sorted by date (newest first)
            statement = select(UserEmails).where(UserEmails.user_id == user_id).order_by(desc(UserEmails.received_at))
            user_emails = session.exec(statement).all()

            # If no records are found, return a 404 error
            if not user_emails:
                logger.warning(f"No emails found for user_id: {user_id}")
                raise HTTPException(
                    status_code=404, detail=f"No emails found for user_id: {user_id}"
                )

            logger.info(
                f"Successfully fetched {len(user_emails)} emails for user_id: {user_id}"
            )
            return user_emails

        except Exception as e:
            logger.error(f"Error fetching emails for user_id {user_id}: {e}")
            raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

def fetch_emails_to_db(user: AuthenticatedUser) -> None:
    global api_call_finished, total_emails, processed_emails

    api_call_finished = False  # this is helpful if the user applies for a new job and wants to rerun the analysis during the same session
    logger.info("user_id:%s fetch_emails_to_db", user.user_id)

    with Session(engine) as session:
        service = build("gmail", "v1", credentials=user.creds)
        messages = get_email_ids(
            query=QUERY_APPLIED_EMAIL_FILTER, gmail_instance=service
        )

        if not messages:
            logger.info(f"user_id:{user.user_id} No job application emails found.")
            return

        logger.info(f"user_id:{user.user_id} Found {len(messages)} emails.")
        total_emails = len(messages)

        email_records = []  # list to collect email records

        for idx, message in enumerate(messages):
            message_data = {}
            # (email_subject, email_from, email_domain, company_name, email_dt)
            msg_id = message["id"]
            logger.info(
                f"user_id:{user.user_id} begin processing for email {idx + 1} of {len(messages)} with id {msg_id}"
            )
            processed_emails = idx + 1

            msg = get_email(message_id=msg_id, gmail_instance=service)

            if msg:
                try:
                    result = process_email(msg["text_content"])
                    # if values are empty strings or null, set them to "unknown"
                    for key in result.keys():
                        if not result[key]:
                            result[key] = "unknown"
                except Exception as e:
                    logger.error(
                        f"user_id:{user.user_id} Error processing email {idx + 1} of {len(messages)} with id {msg_id}: {e}"
                    )

                if not isinstance(result, str) and result:
                    logger.info(
                        f"user_id:{user.user_id} successfully extracted email {idx + 1} of {len(messages)} with id {msg_id}"
                    )
                else:
                    logger.warning(
                        f"user_id:{user.user_id} failed to extract email {idx + 1} of {len(messages)} with id {msg_id}"
                    )
                    result = {"company_name": "unknown", "application_status": "unknown", "job_title": "unknown"}

                message_data = {
                    "id": msg_id,
                    "company_name": result.get("company_name", "unknown"),
                    "application_status": result.get("application_status", "unknown"),
                    "received_at": msg.get("date", "unknown"),
                    "subject": msg.get("subject", "unknown"),
                    "job_title": result.get("job_title", "unknown"),
                    "from": msg.get("from", "unknown"),
                }
                email_record = create_user_email(user, message_data)
                if email_record:
                    email_records.append(email_record)

        # batch insert all records at once
        if email_records:
            session.add_all(email_records)
            session.commit()
            logger.info(
                f"Added {len(email_records)} email records for user {user.user_id}"
            )

        api_call_finished = True
        logger.info(f"user_id:{user.user_id} Email fetching complete.")
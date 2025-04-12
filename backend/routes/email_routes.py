import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, Request, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from sqlmodel import Session, select, desc
from googleapiclient.discovery import build
from db.user_emails import UserEmails
from db import processing_tasks as task_models
from db.utils.user_email_utils import create_user_email
from utils.auth_utils import AuthenticatedUser
from utils.email_utils import get_email_ids, get_email
from utils.llm_utils import process_email
from utils.config_utils import get_settings
from session.session_layer import validate_session
from database import engine
from google.oauth2.credentials import Credentials
import json
from start_date.storage import get_start_date_email_filter
from constants import QUERY_APPLIED_EMAIL_FILTER
from datetime import datetime
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

# Logger setup
logger = logging.getLogger(__name__)

# Get settings
settings = get_settings()
APP_URL = settings.APP_URL

total_emails = 0
processed_emails = 0

# FastAPI router for email routes
router = APIRouter()

@router.get("/processing", response_class=HTMLResponse)
async def processing(request: Request, user_id: str = Depends(validate_session)):
    logging.info("user_id:%s processing", user_id)
    global total_emails, processed_emails
    if not user_id:
        logger.info("user_id: not found, redirecting to login")
        return RedirectResponse("/logout", status_code=303)

    with Session(engine) as session:
        process_task_run = session.get(task_models.TaskRuns, user_id)
        api_call_finished = process_task_run.status == task_models.FINISHED

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
@limiter.limit("5/minute")
def query_emails(request: Request, user_id: str = Depends(validate_session)) -> None:
    with Session(engine) as session:
        try:
            logger.info(f"Fetching emails for user_id: {user_id}")

            # Query emails sorted by date (newest first)
            statement = select(UserEmails).where(UserEmails.user_id == user_id).order_by(desc(UserEmails.received_at))
            user_emails = session.exec(statement).all()

            logger.info(f"Found {len(user_emails)} emails for user_id: {user_id}")
            return user_emails  # Return empty list if no emails exist

        except Exception as e:
            logger.error(f"Error fetching emails for user_id {user_id}: {e}")
            raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
        

@router.delete("/delete-email/{email_id}")
async def delete_email(email_id: str, user_id: str = Depends(validate_session)):
    """
    Delete an email record by its ID for the authenticated user.
    """
    with Session(engine) as session:
        try:
            # Query the email record to ensure it exists and belongs to the user
            email_record = session.exec(
                select(UserEmails).where(
                    (UserEmails.id == email_id) & (UserEmails.user_id == user_id)
                )
            ).first()

            if not email_record:
                logger.warning(f"Email with id {email_id} not found for user_id {user_id}")
                raise HTTPException(
                    status_code=404, detail=f"Email with id {email_id} not found"
                )

            # Delete the email record
            session.delete(email_record)
            session.commit()

            logger.info(f"Email with id {email_id} deleted successfully for user_id {user_id}")
            return {"message": "Item deleted successfully"}

        except Exception as e:
            logger.error(f"Error deleting email with id {email_id} for user_id {user_id}: {e}")
            raise HTTPException(
                status_code=500, detail=f"Failed to delete email: {str(e)}"
            )
        

@router.post("/fetch-emails")
@limiter.limit("5/minute")
async def start_fetch_emails(
    request: Request, background_tasks: BackgroundTasks, user_id: str = Depends(validate_session)
):
    """Starts the background task for fetching and processing emails."""
    
    if not user_id:
        raise HTTPException(status_code=403, detail="Unauthorized")
    logger.info(f"user_id:{user_id} start_fetch_emails")
    # Retrieve stored credentials
    creds_json = request.session.get("creds")
    if not creds_json:
        logger.error(f"Missing credentials for user_id: {user_id}")
        return HTMLResponse(content="User not authenticated. Please log in again.", status_code=401)

    try:
        # Convert JSON string back to Credentials object
        creds_dict = json.loads(creds_json)
        creds = Credentials.from_authorized_user_info(creds_dict)  # Convert dict to Credentials
        user = AuthenticatedUser(creds)

        logger.info(f"Starting email fetching process for user_id: {user_id}")

        # Start email fetching in the background
        background_tasks.add_task(fetch_emails_to_db, user, request)

        return JSONResponse(content={"message": "Email fetching started"}, status_code=200)
    except Exception as e:
        logger.error(f"Error reconstructing credentials: {e}")
        raise HTTPException(status_code=500, detail="Failed to authenticate user")


def fetch_emails_to_db(user: AuthenticatedUser, request: Request, last_updated: Optional[datetime] = None, user_id: str = Depends(validate_session)) -> None:
    global total_emails, processed_emails
    logger.info(f"Fetching emails to db for user_id: {user_id}")

    with Session(engine) as session:
        process_task_run = (
            session.query(task_models.TaskRuns).filter_by(user_id=user_id).one_or_none()
        )
        if process_task_run is None:
            process_task_run = task_models.TaskRuns(user_id=user_id)
        process_task_run.status = task_models.STARTED  # this is helpful if the user applies for a new job and wants to rerun the analysis during the same session
        session.commit()

    start_date = request.session.get("start_date")
    start_date_query = get_start_date_email_filter(start_date)
    is_new_user = request.session.get("is_new_user")

    query = start_date_query
    with Session(engine) as session:
        # check for users last updated email
        if last_updated:
            # this converts our date time to number of seconds 
            additional_time = int(last_updated.timestamp())
            # we append it to query so we get only emails recieved after however many seconds
            # for example, if the newest email you’ve stored was received at 2025‑03‑20 14:32 UTC, we convert that to 1710901920s 
            # and tell Gmail to fetch only messages received after March 20, 2025 at 14:32 UTC.
            if not start_date or not is_new_user:
                query = QUERY_APPLIED_EMAIL_FILTER
                query += f" after:{additional_time}"
            
                logger.info(f"user_id:{user_id} Fetching emails after {last_updated.isoformat()}")
        else:
            logger.info(f"user_id:{user_id} Fetching all emails (no last_date maybe with start date)")
            logger.info(
                f"user_id:{user_id} Fetching all emails (no last_date maybe with start date)"
            )

        service = build("gmail", "v1", credentials=user.creds)

        messages = get_email_ids(
            query=query, gmail_instance=service
        )
        # Update session to remove "new user" status
        request.session["is_new_user"] = False

        if not messages:
            logger.info(f"user_id:{user_id} No job application emails found.")
            with Session(engine) as session:
                process_task_run = session.get(task_models.TaskRuns, user_id)
                process_task_run.status = task_models.FINISHED
                session.commit()
            return

        logger.info(f"user_id:{user.user_id} Found {len(messages)} emails.")
        total_emails = len(messages)

        email_records = []  # list to collect email records

        for idx, message in enumerate(messages):
            message_data = {}
            # (email_subject, email_from, email_domain, company_name, email_dt)
            msg_id = message["id"]
            logger.info(
                f"user_id:{user_id} begin processing for email {idx + 1} of {len(messages)} with id {msg_id}"
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
                        f"user_id:{user_id} Error processing email {idx + 1} of {len(messages)} with id {msg_id}: {e}"
                    )

                if not isinstance(result, str) and result:
                    logger.info(
                        f"user_id:{user_id} successfully extracted email {idx + 1} of {len(messages)} with id {msg_id}"
                    )
                else:
                    logger.warning(
                        f"user_id:{user_id} failed to extract email {idx + 1} of {len(messages)} with id {msg_id}"
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
                f"Added {len(email_records)} email records for user {user_id}"
            )

        with Session(engine) as session:
            process_task_run = session.get(task_models.TaskRuns, user_id)
            process_task_run.status = task_models.FINISHED
            session.commit()
        logger.info(f"user_id:{user_id} Email fetching complete.")

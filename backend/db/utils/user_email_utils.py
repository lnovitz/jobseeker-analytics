from db.user_email import UserEmail
from datetime import datetime, timezone
import email.utils
import logging
from database import engine
from sqlmodel import Session, select

logger = logging.getLogger(__name__)

def parse_email_date(date_str: str) -> datetime:
    """
    Converts an email date string into a Python datetime object
    """
    dt = email.utils.parsedate_to_datetime(date_str)
    if dt is None:
        # default to current UTC datetime
        dt = datetime.now(timezone.utc)
    return dt


def check_email_exists(user_id: str, email_id: str) -> bool:
    """
    Checks if an email with the given emailId and userId exists in the database.
    """
    with Session(engine) as session:
        statement = select(UserEmail).where(
            (UserEmail.user_id == user_id) & (UserEmail.id == email_id)
        )
        result = session.exec(statement).first()
        return result is not None


def create_user_email(user, message_data: dict) -> UserEmail:
    """
    Creates a UserEmail record instance from the provided data.
    """
    received_at_str = message_data["received_at"]
    received_at = parse_email_date(received_at_str)  # parse_email_date function was created as different date formats were being pulled from the data
    if check_email_exists(user.user_id, message_data["id"]):
        logger.info(f"Email with ID {message_data['id']} already exists in the database.")
        return None
    return UserEmail(
        id=message_data["id"],
        user_id=user.user_id,
        company_name=message_data["company_name"],
        application_status=message_data["application_status"],
        received_at=received_at,
        subject=message_data["subject"],
        email_from=message_data["from"]
    )

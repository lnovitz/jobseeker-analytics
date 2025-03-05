from sqlmodel import Session
from db.user_email import UserEmail
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def add_user_email(user, message_data: dict, session: Session) -> None:
    """
    Insert email record into the user_emails table.
    """
    received_at_str = message_data["received_at"][0]
    received_at = datetime.strptime(received_at_str, "%Y-%m-%d %H:%M:%S")
    
    email_record = UserEmail(
    user_id=user.user_id,
    company_name=message_data["company_name"][0],
    application_status=message_data["application_status"][0],
    received_at=received_at,
    subject=message_data["subject"][0],
    email_from=message_data["from"][0]
    )
    session.add(email_record)
    session.commit()
    session.refresh(email_record)
    logger.info(f"Added email record for user {user.user_id}")
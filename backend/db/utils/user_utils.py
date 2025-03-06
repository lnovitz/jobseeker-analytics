import logging
from sqlmodel import Session, select
from users import Users 
from datetime import datetime, timedelta, timezone

logger = logging.getLogger(__name__)

def user_is_in_database(user, session: Session) -> bool:
    """
    Checks if user is already in the database

    """
    existing_user = session.exec(select(Users).where(Users.user_id == user.user_id)).first()
    if not existing_user:
        return False
    else:
        return True

def add_user(user, start_date: datetime, session: Session) -> Users:
    """
    Writes user data to the users model

    """
    # Check if the user already exists in the database
    existing_user = session.exec(select(Users).where(Users.user_id == user.user_id)).first()

    if not existing_user:
        # add a new user record
        new_user = Users(
            user_id=user.user_id,
            user_email=user.user_email,
            google_openid=user.google_openid,
            start_date=start_date
        )

        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        logger.info(f"Created new user record for user_id: {user.user_id}")
        return new_user
    else:
        logger.info(f"User {user.user_id} already exists in the database.")
        return existing_user

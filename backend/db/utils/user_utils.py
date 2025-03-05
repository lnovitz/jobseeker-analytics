import logging
from sqlmodel import Session, select
from db.users import Users  # Adjust the import to your project structure

logger = logging.getLogger(__name__)

def add_user(user, session: Session) -> Users:
    """
    Writes user data to the users model upon login.
    
    """
    # check if the user already exists in the database
    existing_user = session.exec(select(Users).where(Users.user_id == user.user_id)).first()
    if not existing_user:
        # if not we just create a new user record
        new_user = Users(
            user_id=user.user_id,
            user_email=user.user_email,
            google_openid=user.google_openid
        )
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        logger.info(f"Created new user record for user_id: {user.user_id}")
        return new_user
    else:
        logger.info(f"User {user.user_id} already exists in the database.")
        return existing_user

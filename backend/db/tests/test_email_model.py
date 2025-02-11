import pytest
from datetime import datetime
from ..database import get_session, create_db_and_tables  
from ..emails import Email
from sqlmodel import select

@pytest.fixture(scope="function")
def db_session():
    """Creates a fresh database session for each test."""
    create_db_and_tables()
    session = get_session()
    yield session  
    session.close()  

@pytest.fixture
def new_email():
    """Fixture to create a new email instance for testing"""
    return Email(
        email_subject="Test Subject",
        from_email="test@example.com",
        company_id=1,
        received_at=datetime.now(),
        user_id=1,
        status_id=1,
    )

def test_create_email(new_email):
    """Test creating a new email instance."""

    assert new_email.email_subject == "Test Subject"
    assert new_email.from_email == "test@example.com"

def test_add_and_query_email(db_session, new_email):
    """Test inserting and querying an email record."""
    
    db_session.add(new_email)
    db_session.commit()

    stmt = select(Email).where(Email.email_id == 1)
    queried_email = db_session.exec(stmt).first()

    assert queried_email is not None, "Email was not found in the database."
    assert queried_email.email_subject == "Test Subject"
    assert queried_email.from_email == "test@example.com"

def test_incrementing_email_ids(db_session):
    """Test that the email_ids auto-increment"""
    email1 = Email(
        email_subject="Test Subject 1",
        from_email="test1@example.com",
        company_id=1,
        received_at=datetime.now(),
        user_id=1,
        status_id=1
    )

    email2 = Email(
        email_subject="Test Subject 2",
        from_email="test2@example.com",
        company_id=2,
        received_at=datetime.now(),
        user_id=2,
        status_id=2
    )

    db_session.add(email1)
    db_session.add(email2)
    db_session.commit()

    assert email1.email_id == 1
    assert email2.email_id == 2

def test_deleting_email(db_session, new_email):
    """Test that an email is successfully deleted from the db"""
    
    db_session.add(new_email)
    db_session.commit()

    db_session.delete(new_email)
    db_session.commit()

    stmt = select(Email).where(Email.email_id == new_email.email_id)
    deleted_email = db_session.exec(stmt).first()

    assert deleted_email is None
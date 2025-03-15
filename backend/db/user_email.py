from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class UserEmail(SQLModel, table=True):
    __tablename__ = "user_email"  
    id: str = Field(primary_key=True)  # Gmail email ID (not unique globally)
    user_id: str = Field(primary_key=True)  # Unique per user (composite key)
    company_name: str
    application_status: str
    received_at: datetime
    subject: str
    email_from: str  # to avoid 'from' being a reserved key word
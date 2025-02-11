from sqlmodel import SQLModel, Field
from datetime import datetime

class Email(SQLModel, table=True):
    __tablename__ = 'emails'
    email_id: int = Field(default=None, primary_key=True)
    email_subject: str
    from_email: str
    company_id: int = Field(foreign_key="company.id")  
    received_at: datetime
    user_id: int = Field(foreign_key="user.id") 
    status_id: int = Field(foreign_key="status.id")
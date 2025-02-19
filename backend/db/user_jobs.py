from sqlmodel import SQLModel, Field
from datetime import datetime

class UserJobs(SQLModel, table=True):
    __tablename__ = "user_jobs"
    user_id: int = Field(foreign_key="users.user_id", nullable=False)
    job_id: int = Field(foreign_key="company_jobs.job_id", nullable=False)
    applied_at: datetime
    

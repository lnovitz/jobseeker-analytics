from sqlmodel import SQLModel, Field

class UserJobStatus(SQLModel, table=True):
    __tablename__ = "user_job_status"
    user_id: int = Field(foreign_key="users.user_id", nullable=False)
    job_id: int = Field(foreign_key="company_jobs.job_id", nullable=False)
    status_id: int = Field(foreign_key="job_status.status_id", nullable=False)
    

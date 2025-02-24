from sqlmodel import SQLModel, Field, UniqueConstraint
from datetime import datetime

class CompanyJobs(SQLModel, table=True):
    __tablename__ = 'company_jobs'
    job_id: int = Field(default=None, primary_key=True)
    company_id: int = Field(foreign_key="companies.company_id", nullable=False)
    job_title_id: int = Field(foreign_key="job_titles.job_title_id", nullable=False)
    job_description: str 
    job_posted_at: datetime 
    job_location: str

    __table_args__ = (
        # Ensure that company_name and company_email_domain together are unique
        UniqueConstraint('company_id', 'job_title_id', 'job_location', name='unique_job_title_and_location'),
    )



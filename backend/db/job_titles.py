from sqlmodel import SQLModel, Field, UniqueConstraint

class JobTitles(SQLModel, table=True):
    __tablename__ = 'job_titles'
    job_title_id: int = Field(default=None, primary_key=True)
    job_title: str 

    __table_args__ = (
        UniqueConstraint('job_title', name='unique_job_title'),
    )

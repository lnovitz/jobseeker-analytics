from sqlmodel import SQLModel, Field

class JobStatus(SQLModel, table=True):
    __tablename__ = 'job_status'
    status_id: int = Field(default=None, primary_key=True)
    status_name: str 
    status_description: str

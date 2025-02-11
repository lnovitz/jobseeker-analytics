from sqlmodel import SQLModel, Field

class CompanyUsers(SQLModel, table=True):
    __tablename__ = 'company_users'
    company_user_id: int = Field(default=None, primary_key=True)
    company_id: int = Field(foreign_key="companies.company_id", nullable=False)
    from_email: str = Field(nullable=False)

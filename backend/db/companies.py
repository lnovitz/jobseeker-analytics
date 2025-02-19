from sqlmodel import SQLModel, Field, UniqueConstraint

class Companies(SQLModel, table=True):
    __tablename__ = 'companies'
    company_id: int = Field(default=None, primary_key=True)
    company_name: str
    company_email_domain: str 

    __table_args__ = (
        # Ensure that company_name and company_email_domain together are unique
        UniqueConstraint('company_name', 'company_email_domain', name='unique_company_name_and_domain'),
    )

    

from sqlmodel import SQLModel, Field

class Users(SQLModel, table=True):
    __tablename__ = "users"
    user_id: int = Field(default = None, primary_key = True)
    user_email: str = Field(nullable=False)                      # nullable=False - shouldn't be null
    user_sheet_url: str = Field(nullable=False, default="")      # Ensures URL is not null

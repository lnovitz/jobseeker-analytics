from pydantic import BaseModel
from sqlmodel import SQLModel, Field

class TestTable(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    __tablename__ = "test_table"

class TestData(BaseModel):
    name: str
from sqlmodel import SQLModel, Field
from uuid import UUID, uuid4
from datetime import datetime, timezone
from typing import Optional

class UserSession(SQLModel, table=True):
    __tablename__ = "user_session"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: int = Field(foreign_key="users.user_id")
    session_start: datetime = Field(default_factory=datetime.now(timezone.utc))
    session_end: Optional[datetime] = None
    user_agent: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now(timezone.utc))
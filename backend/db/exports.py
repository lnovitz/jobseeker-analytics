from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional
from pydantic import field_validator

class Exports(SQLModel, table=True):
    export_id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int 
    export_type_id: int = Field(index=True)  # this will determine if URL is allowed
    export_url: Optional[str] = Field(default=None, nullable=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @field_validator("export_url")
    def validate_export_url(cls, value, values):
        """
        Enforce that export_url is only allowed if export_type_id corresponds to Google Sheets.
        """
        GOOGLE_SHEET_TYPE_ID = 1  # google sheet type id
        
        # if export_url is provided, ensure export_type_id is google sheets
        if value and values.get("export_type_id") != GOOGLE_SHEET_TYPE_ID:
            raise ValueError("export_url can only be set for Google Sheets exports.")
        
        return value
    
    def __init__(self, **kwargs):
        """Ensure validation runs on object creation."""
        super().__init__(**kwargs)  
        self.validate_export_url(self.export_url, kwargs)  
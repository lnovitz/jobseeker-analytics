from sqlmodel import SQLModel, Field
from enum import Enum

class ExportTypeName(str, Enum):
    csv_download = "csv_download"
    google_sheets_export = "google_sheets_export"

class ExportType(SQLModel, table=True):
    __tablename__ = "export_types"
    export_type_id = int = Field(default=None, primary_key=True)
    export_type_name = ExportTypeName
    export_type_description = str
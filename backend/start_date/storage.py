"""
This file contains the main constants used in the application.
"""
from pathlib import Path
from utils.filter_utils import (
    parse_base_filter_config,
)


APPLIED_FILTER_PATH = (
    Path(__file__).parent.parent / "email_query_filters" / "applied_email_filter.yaml"
)

def get_start_date_email_filter(start_date: str) -> str:

    START_DATE_EMAIL_FILTER = (
        f"after:{start_date} AND ({parse_base_filter_config(APPLIED_FILTER_PATH)})"
    )
    return START_DATE_EMAIL_FILTER
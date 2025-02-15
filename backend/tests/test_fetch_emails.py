from unittest import mock
from unittest.mock import MagicMock
from google.oauth2.credentials import Credentials

from utils.auth_utils import AuthenticatedUser
from main import fetch_emails
from constants import QUERY_APPLIED_EMAIL_FILTER

# mocked Data
dummy_creds = MagicMock(spec=Credentials)
dummy_creds.id_token = "dummy_id_token"

mock_user = AuthenticatedUser(creds=dummy_creds)

mock_messages = [
    {"id": "msg_1"},
]

mock_message_one = {
    "id": "msg_1",
    "text_content": "email contents",
    "date": "2025-02-14",
    "subject": "Job Application",
    "from": "company@example.com",
}

mock_processed_result = {
    "company_name": "Test Company",
    "application_status": "offer",
}

@mock.patch("main.get_email_ids", return_value=mock_messages)
@mock.patch("main.get_email", return_value=mock_message_one)
@mock.patch("main.process_email", return_value=mock_processed_result)
@mock.patch("main.export_to_csv")
@mock.patch("main.logger")

def test_fetch_emails(mock_logger, mock_export_to_csv, mock_process_email, mock_get_email, mock_get_email_ids):
    # Call the fetch_emails function
    fetch_emails(mock_user)

    # Assert that get_email_ids was called once
    mock_get_email_ids.assert_called_once_with(query=QUERY_APPLIED_EMAIL_FILTER, gmail_instance=mock.ANY)

    # Assert that get_email was called for each message id
    mock_get_email.assert_any_call(message_id="msg_1", gmail_instance=mock.ANY)

    # Assert that process_email was called with the email's text contents
    mock_process_email.assert_called_with("email contents")

    # Assert that export_to_csv was called once with the email data
    mock_export_to_csv.assert_called_once_with(mock_user.filepath, mock_user.user_id, {
        "company_name": ["Test Company"],
        "application_status": ["offer"],
        "received_at": ["2025-02-14"],
        "subject": ["Job Application"],
        "from": ["company@example.com"],
    })

    mock_logger.info.assert_called_with("user_id:%s email fetching complete", mock_user.user_id)

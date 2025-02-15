import main
from unittest import mock
from unittest.mock import MagicMock
from google.oauth2.credentials import Credentials

from utils.auth_utils import AuthenticatedUser
from main import fetch_emails
from constants import QUERY_APPLIED_EMAIL_FILTER

# mocked data
dummy_creds = MagicMock(spec=Credentials)
dummy_creds.id_token = "dummy_id_token"

mock_user = AuthenticatedUser(creds=dummy_creds)

# one message fetched and processed correctly.

mock_messages_success = [{"id": "msg_1"}]
mock_message_success = {
    "id": "msg_1",
    "text_content": "email contents",
    "date": "2025-02-14",
    "subject": "Job Application",
    "from": "company@example.com",
}
mock_processed_result_success = {
    "company_name": "Test Company",
    "application_status": "offer",
}


# test 1: successful processing 
@mock.patch("main.get_email_ids", return_value=mock_messages_success)
@mock.patch("main.get_email", return_value=mock_message_success)
@mock.patch("main.process_email", return_value=mock_processed_result_success)
@mock.patch("main.export_to_csv")
@mock.patch("main.logger")

def test_fetch_emails(mock_logger, mock_export_to_csv, mock_process_email, mock_get_email, mock_get_email_ids):
    # call the fetch_emails function
    fetch_emails(mock_user)

    # assert that get_email_ids was called once
    mock_get_email_ids.assert_called_once_with(query=QUERY_APPLIED_EMAIL_FILTER, gmail_instance=mock.ANY)
    # assert that get_email was called for each message id
    mock_get_email.assert_any_call(message_id="msg_1", gmail_instance=mock.ANY)
    # assert that process_email was called with the email's text contents
    mock_process_email.assert_called_with("email contents")

    # assert that export_to_csv was called once with the email data
    mock_export_to_csv.assert_called_once_with(mock_user.filepath, mock_user.user_id, {
        "company_name": ["Test Company"],
        "application_status": ["offer"],
        "received_at": ["2025-02-14"],
        "subject": ["Job Application"],
        "from": ["company@example.com"],
    })

    mock_logger.info.assert_called_with("user_id:%s email fetching complete", mock_user.user_id)

# test 2: email fetch failure 
@mock.patch("main.get_email_ids", return_value=mock_messages_success)
@mock.patch("main.get_email", return_value=None)
@mock.patch("main.process_email")
@mock.patch("main.export_to_csv")
@mock.patch("main.logger")
def test_fetch_emails_email_fetch_fail(mock_logger, mock_export_to_csv, mock_process_email, mock_get_email, mock_get_email_ids):

    main.api_call_finished = None
    fetch_emails(mock_user)

    # since get_email returned None, process_email should not be called.
    mock_get_email.assert_called_once_with(message_id="msg_1", gmail_instance=mock.ANY)
    mock_process_email.assert_not_called()

    # export_to_csv should not be called because we skipped this message.
    mock_export_to_csv.assert_not_called()

    # a warning should be logged.
    mock_logger.warning.assert_called_once()
    assert main.api_call_finished is True


# test 3: processing failure
@mock.patch("main.get_email_ids", return_value=mock_messages_success)
@mock.patch("main.get_email", return_value=mock_message_success)
@mock.patch("main.process_email", return_value="invalid") 
@mock.patch("main.export_to_csv")
@mock.patch("main.logger")
def test_fetch_emails_process_email_returns_string(
    mock_logger, mock_export_to_csv, mock_process_email, mock_get_email, mock_get_email_ids):
    main.api_call_finished = None
    fetch_emails(mock_user)

    mock_process_email.assert_called_with("email contents")
    # since process_email returned a string, it triggers the "failure" branch and resets result to {}.
    expected_data = {
        "company_name": [""],
        "application_status": [""],
        "received_at": ["2025-02-14"],
        "subject": ["Job Application"],
        "from": ["company@example.com"],
    }
    mock_export_to_csv.assert_called_once_with(mock_user.filepath, mock_user.user_id, expected_data)
    #logger.info should have been called for extraction failure.
    mock_logger.info.assert_any_call("user_id:%s failed to extract email", mock_user.user_id)
    assert main.api_call_finished is True


# test 4: exception handling
@mock.patch("main.get_email_ids", side_effect=Exception("Test Exception"))
@mock.patch("main.logger")
def test_fetch_emails_exception(mock_logger, mock_get_email_ids):
    main.api_call_finished = None
    fetch_emails(mock_user)

    # an error should be logged, and api_call_finished should be set to False.
    mock_logger.error.assert_called()
    assert main.api_call_finished is False
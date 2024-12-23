from tests.constants import SAMPLE_MESSAGE
import email_utils
from unittest import mock


def test_get_email_subject_line():
    subject_line = email_utils.get_email_subject_line(SAMPLE_MESSAGE)
    assert (
        subject_line
        == "Invitation from an unknown sender: Interview with TestCompanyName @ Thu May 2, 2024 11:00am - 12pm (PDT) (appuser@gmail.com)"
    )


def test_get_email_from_address():
    from_address = email_utils.get_email_from_address(SAMPLE_MESSAGE)
    assert from_address == "recruitername@testcompanyname.com"


def test_get_email_domain():
    from_email_domain = email_utils.get_email_domain_from_address(
        "recruitername@testcompanyname.com"
    )
    assert from_email_domain == "testcompanyname.com"


def test_get_company_name_returns_email_domain():
    company_name = email_utils.get_company_name(SAMPLE_MESSAGE)
    assert company_name == "testcompanyname"


def test_get_company_name_returns_top_word():
    """Default behavior for company name is to return the highest frequency word that appears in the email body."""
    with mock.patch("email_utils.get_top_word_in_email_body", return_value="fake"):
        company_name = email_utils.get_company_name(SAMPLE_MESSAGE)
        assert company_name == "fake"


def test_get_email_received_at_timestamp():
    received_at = email_utils.get_received_at_timestamp(1, SAMPLE_MESSAGE)
    assert received_at == "Thu, 2 May 2024 16:45:00 +0000"

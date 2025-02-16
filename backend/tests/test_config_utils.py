from unittest.mock import patch
from utils.config_utils import get_settings
from config import Settings
import pytest
import json
import os


@pytest.fixture(scope="session", autouse=True)
def setup_static_directory():
    static_dir = os.path.join(os.path.dirname(__file__), "../static")
    if not os.path.exists(static_dir):
        os.makedirs(static_dir)



@patch("utils.config_utils.config.Settings")
def test_get_settings_only_called_once_with_lru(mock_settings_call):
    get_settings.cache_clear()
    get_settings()
    get_settings()
    # Ensure the Settings constructor is called only once due to lru_cache
    mock_settings_call.assert_called_once()
    get_settings.cache_clear()


def test_import_settings_does_not_raise_error():
    import backend.utils.llm_utils  # noqa: F401
    import backend.utils.auth_utils  # noqa: F401


def test_decode_scopes_valid_json():
    input_str = '["https://www.googleapis.com/auth/gmail.readonly", "openid"]'
    expected_output = ["https://www.googleapis.com/auth/gmail.readonly", "openid"]
    assert Settings.decode_scopes(input_str) == expected_output


def test_decode_scopes_with_extra_quotes():
    input_str = '\'["https://www.googleapis.com/auth/gmail.readonly", "openid"]\''
    expected_output = ["https://www.googleapis.com/auth/gmail.readonly", "openid"]
    assert Settings.decode_scopes(input_str) == expected_output


def test_decode_scopes_invalid_json():
    input_str = '["https://www.googleapis.com/auth/gmail.readonly", "openid"'
    with pytest.raises(json.JSONDecodeError):
        Settings.decode_scopes(input_str)


def test_decode_scopes_empty_string():
    input_str = ""
    with pytest.raises(json.JSONDecodeError):
        Settings.decode_scopes(input_str)

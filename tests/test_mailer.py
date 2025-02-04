"""
tests/test_mailer.py
Tests sending a simple email with Python and Gmail.
"""

import os
import pytest
from unittest.mock import patch, MagicMock
from dc_mailer.mailer import send_mail
from dc_mailer.config import load_config

# Sample TOML config as a string
SAMPLE_TOML_CONFIG = """
outgoing_email_host = "smtp.example.com"
outgoing_email_port = "587"
outgoing_email_address = "user@example.com"
outgoing_email_password = "securepassword"
"""


@pytest.fixture
def temp_config_file(tmp_path):
    """Creates a temporary .env.toml file for testing."""
    config_file = tmp_path / ".env.toml"
    config_file.write_text(SAMPLE_TOML_CONFIG)
    return config_file


@pytest.fixture
def clear_env_vars(monkeypatch):
    """Clears all environment variables related to outgoing email."""
    for key in os.environ.keys():
        if key.startswith("OUTGOING_"):
            monkeypatch.delenv(key, raising=False)


@pytest.fixture
def mock_smtp(monkeypatch):
    """Mocks SMTP and SMTP_SSL to prevent actual email sending."""
    with (
        patch("dc_mailer.mailer.smtplib.SMTP") as mock_smtp,
        patch("dc_mailer.mailer.smtplib.SMTP_SSL") as mock_smtp_ssl,
    ):
        mock_server = MagicMock()

        # Configure the mock behavior
        mock_smtp.return_value.__enter__.return_value = mock_server
        mock_smtp_ssl.return_value.__enter__.return_value = mock_server
        mock_server.login.return_value = True
        mock_server.send_message.return_value = None

        yield mock_smtp, mock_smtp_ssl, mock_server


def test_no_env_no_file(monkeypatch):
    """Test when neither environment variables nor a file exist."""
    for key in os.environ.keys():
        if key.startswith("OUTGOING_"):
            monkeypatch.delenv(key, raising=False)

    with pytest.raises(
        RuntimeError, match="Please provide required configuration variables."
    ):
        load_config()

def test_env_vars_only(monkeypatch):
    """Test when only environment variables exist, no config file."""
    monkeypatch.setenv("OUTGOING_EMAIL_HOST", "smtp.env.com")
    monkeypatch.setenv("OUTGOING_EMAIL_PORT", "465")
    monkeypatch.setenv("OUTGOING_EMAIL_ADDRESS", "env_user@example.com")
    monkeypatch.setenv("OUTGOING_EMAIL_PASSWORD", "envpassword")

    config = load_config()
    assert config["outgoing_email_host"] == "smtp.env.com"
    assert config["outgoing_email_port"] == "465"
    assert config["outgoing_email_address"] == "env_user@example.com"
    assert config["outgoing_email_password"] == "envpassword"


def test_file_only(temp_config_file, monkeypatch):
    """Test when only a config file exists, no environment variables."""
    for key in os.environ.keys():
        if key.startswith("OUTGOING_"):
            monkeypatch.delenv(key, raising=False)

    config = load_config(config_file=str(temp_config_file))
    assert config["outgoing_email_host"] == "smtp.example.com"
    assert config["outgoing_email_port"] == "587"
    assert config["outgoing_email_address"] == "user@example.com"
    assert config["outgoing_email_password"] == "securepassword"


def test_both_env_and_file(temp_config_file, monkeypatch):
    """Test when both environment variables and a file exist, env vars take priority."""
    monkeypatch.setenv("OUTGOING_EMAIL_HOST", "smtp.override.com")
    monkeypatch.setenv("OUTGOING_EMAIL_PORT", "2525")
    monkeypatch.setenv("OUTGOING_EMAIL_ADDRESS", "override_user@example.com")
    monkeypatch.setenv("OUTGOING_EMAIL_PASSWORD", "overridepassword")

    config = load_config(config_file=str(temp_config_file))

    assert config["outgoing_email_host"] == "smtp.override.com"
    assert config["outgoing_email_port"] == "2525"
    assert config["outgoing_email_address"] == "override_user@example.com"
    assert config["outgoing_email_password"] == "overridepassword"


@pytest.mark.parametrize(
    "subject, body, recipient, port",
    [
        (
            "Test Subject 1",
            "Test message 1",
            "recipient@example.com",
            465,
        ),  # SMTP_SSL expected
        (
            "Alert",
            "Hello, this is a test!",
            "recipient@example.com",
            587,
        ),  # SMTP with TLS expected
        (
            "Python Notification",
            "Email alert from Python program",
            "recipient@example.com",
            2525,
        ),  # Uncommon port
    ],
)
def test_send_mail_mocked(subject, body, recipient, port, monkeypatch, mock_smtp):
    """Test send_mail() with mocked SMTP client."""
    mock_smtp, mock_smtp_ssl, mock_server = mock_smtp

    monkeypatch.setenv("OUTGOING_EMAIL_HOST", "smtp.example.com")
    monkeypatch.setenv("OUTGOING_EMAIL_PORT", str(port))  # Ensure correct port
    monkeypatch.setenv("OUTGOING_EMAIL_ADDRESS", "user@example.com")
    monkeypatch.setenv("OUTGOING_EMAIL_PASSWORD", "securepassword")

    try:
        send_mail(subject=subject, body=body, recipient=recipient)

        # Ensure correct SMTP class is used
        if port == 465:
            mock_smtp_ssl.assert_called_once()
        else:
            mock_smtp.assert_called_once()

        mock_server.login.assert_called_once()
        mock_server.send_message.assert_called_once()

    except Exception as e:
        pytest.fail(f"send_mail() raised an exception: {e}")


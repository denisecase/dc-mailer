"""
tests/test_config.py
Tests for retrieving configuration variables for emailing via Python and Gmail.
"""

import pathlib
import shutil
import pytest
import os


from dc_mailer.config import (
    load_config,
    get_config_from_env,
    load_config_from_file,
    merge_configs,
)

# Sample TOML config as a string
SAMPLE_TOML_CONFIG = """
outgoing_email_host = "smtp.example.com"
outgoing_email_port = "587"
outgoing_email_address = "user@example.com"
outgoing_email_password = "securepassword"
"""


@pytest.fixture(scope="session", autouse=True)
def backup_and_restore_env_file():
    """
    Before running tests:
    - Rename `.env.toml` to `.env.toml.bak` (if it exists).

    After tests finish:
    - Restore `.env.toml` back from `.env.toml.bak`.
    """
    env_file = pathlib.Path(".env.toml")
    backup_file = pathlib.Path(".env.toml.bak")

    # Backup `.env.toml` if it exists
    if env_file.exists():
        shutil.move(str(env_file), str(backup_file))

    yield  # Run the tests

    # Restore `.env.toml` after tests
    if backup_file.exists():
        shutil.move(str(backup_file), str(env_file))


@pytest.fixture
def temp_config_file(tmp_path):
    """Create temporary .env.toml file for testing."""
    config_file = tmp_path / ".env.toml"
    config_file.write_text(SAMPLE_TOML_CONFIG)
    return config_file


def test_no_env_no_file(monkeypatch, tmp_path):
    """Test when neither environment variables nor a file exist."""

    # Remove ALL relevant ENV variables
    for key in list(os.environ.keys()):
        if key.startswith("OUTGOING_"):
            monkeypatch.delenv(key, raising=False)

    original_exists = pathlib.Path.exists

    def mock_path_exists(path):
        if ".env.toml" in str(path):
            return False
        return original_exists(path)

    monkeypatch.setattr(pathlib.Path, "exists", mock_path_exists)

    # Use an empty temp directory as config path
    temp_config_path = tmp_path / ".env.toml"
    assert not temp_config_path.exists()

    with pytest.raises(
        RuntimeError, match="Please provide required configuration variables."
    ):
        load_config(config_file=str(temp_config_path))


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
    """Test when both environment variables and a file exist, ENV vars take priority."""
    # Set environment variables that should OVERRIDE file values
    monkeypatch.setenv("OUTGOING_EMAIL_HOST", "smtp.override.com")
    monkeypatch.setenv("OUTGOING_EMAIL_PORT", "2525")
    monkeypatch.setenv("OUTGOING_EMAIL_ADDRESS", "override_user@example.com")
    monkeypatch.setenv("OUTGOING_EMAIL_PASSWORD", "overridepassword")

    config = load_config(config_file=str(temp_config_file))

    # ENV VARS should take priority over file config
    assert config["outgoing_email_host"] == "smtp.override.com"
    assert config["outgoing_email_port"] == "2525"
    assert config["outgoing_email_address"] == "override_user@example.com"
    assert config["outgoing_email_password"] == "overridepassword"


def test_merge_configs():
    """Test merging ENV and file configurations, ensuring ENV takes priority."""
    env_config = {
        "outgoing_email_host": "smtp.env.com",
        "outgoing_email_port": "465",
    }
    file_config = {
        "outgoing_email_host": "smtp.file.com",
        "outgoing_email_port": "587",
        "outgoing_email_address": "file_user@example.com",
    }

    merged_config = merge_configs(env_config, file_config)

    # ENV should override file values
    assert merged_config["outgoing_email_host"] == "smtp.env.com"
    assert merged_config["outgoing_email_port"] == "465"

    # File should provide values not present in ENV
    assert merged_config["outgoing_email_address"] == "file_user@example.com"


def test_get_config_from_env(monkeypatch):
    """Test retrieving config from environment variables."""
    monkeypatch.setenv("OUTGOING_EMAIL_HOST", "smtp.env.com")
    monkeypatch.setenv("OUTGOING_EMAIL_PORT", "465")

    config = get_config_from_env()
    assert config["outgoing_email_host"] == "smtp.env.com"
    assert config["outgoing_email_port"] == "465"


def test_load_config_from_file(temp_config_file):
    """Test loading config from a TOML file."""
    config = load_config_from_file(temp_config_file)

    assert config["outgoing_email_host"] == "smtp.example.com"
    assert config["outgoing_email_port"] == "587"

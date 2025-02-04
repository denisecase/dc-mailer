"""
dc_mailer/config.py
Get configuration variables for sending email via Gmail.
"""

import os
import logging
import tomllib
from pathlib import Path

# Configure logging format
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Define the mapping between config keys and environment variable names
ENV_VAR_MAPPING = {
    "outgoing_email_host": "OUTGOING_EMAIL_HOST",
    "outgoing_email_port": "OUTGOING_EMAIL_PORT",
    "outgoing_email_address": "OUTGOING_EMAIL_ADDRESS",
    "outgoing_email_password": "OUTGOING_EMAIL_PASSWORD",
}


def get_config_from_env() -> dict:
    """Retrieve configuration values from environment variables."""
    config = {
        key: os.getenv(env_var)
        for key, env_var in ENV_VAR_MAPPING.items()
        if os.getenv(env_var)
    }

    if config:
        logging.info(f"Loaded {len(config)} variables from ENV.")
    return config


def get_default_config_paths() -> list:
    """Return a list of possible config file locations."""
    script_dir = Path(__file__).resolve().parent
    return [
        script_dir / ".env.toml",  # Package install directory
        Path.cwd() / ".env.toml",  # Current working directory
    ]


def load_config_from_file(config_file: Path) -> dict:
    """Load configuration values from a TOML file."""
    if not config_file.exists():
        logging.warning(f"Config file {config_file} not found.")
        return {}

    try:
        with config_file.open("rb") as file:
            file_config = tomllib.load(file)
            loaded_config = {
                key: file_config.get(key)
                for key in ENV_VAR_MAPPING.keys()
                if key in file_config
            }

            logging.info(f"Loaded {len(loaded_config)} variables from {config_file}.")
            return loaded_config
    except Exception as e:
        logging.error(f"Error loading config file {config_file}: {e}")
        return {}


def merge_configs(env_config: dict, file_config: dict) -> dict:
    """Merge environment and file configurations, prioritizing environment variables."""
    merged_config = env_config.copy()
    merged_config.update(
        {k: v for k, v in file_config.items() if k not in merged_config}
    )

    return merged_config


def load_config(config_file: str = None) -> dict:
    """
    Load settings from environment variables or a .env.toml file.

    Prioritizes:
    1. Environment variables.
    2. User-specified `config_file` if provided.
    3. `.env.toml` in the package install directory.
    4. `.env.toml` in the current working directory.
    5. Raises a `RuntimeError` if no valid config is found.
    """
    env_config = get_config_from_env()

    # If all values are found in environment variables, return immediately
    if len(env_config) == len(ENV_VAR_MAPPING):
        return env_config

    # Determine config file paths
    possible_paths = (
        [Path(config_file).expanduser().resolve()]
        if config_file
        else get_default_config_paths()
    )
    found_file_config = {}

    for path in possible_paths:
        logging.info(f"Checking for config file: {path}")
        file_config = load_config_from_file(path)
        if file_config:
            found_file_config = file_config
        merged_config = merge_configs(env_config, found_file_config)

    logging.info(f"Loaded {len(merged_config)} variables from {possible_paths}.")
    missing_keys = [key for key in ENV_VAR_MAPPING.keys() if key not in merged_config]
    logging.info(f"Missing keys: {missing_keys}")
    if missing_keys:
        logging.error(
            f"Config loading failed. Missing keys: {missing_keys}. "
            f"Checked ENV variables: {env_config}. Checked files: {possible_paths}."
        )
        raise RuntimeError("Please provide required configuration variables.")

    return merged_config


if __name__ == "__main__":
    logging.info("Initializing Configuration Loader...")

    try:
        data = load_config()
        logging.info(f"SUCCESS: Loaded {len(data)} configuration variables.")
    except RuntimeError as e:
        logging.error(f"ERROR: Configuration loading failed. {e}")

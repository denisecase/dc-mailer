"""
Send an email with Python and Gmail.

Author: Denise Case
Date: 2022-12-27
Updated: 2025-02-02
"""

import os
import logging
import smtplib
import tomllib
from email.message import EmailMessage
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def load_config(config_file: str = None):
    """
    Load settings from environment variables or a .env.toml file.

    Prioritizes:
    1. Environment variables.
    2. User-specified absolute `config_file` (if provided).
    3. `.env.toml` located in the package install directory.
    4. `.env.toml` in the current working directory.
    5. Raises a `RuntimeError` if no valid config is found.
    """

    # Define the mapping between config keys and environment variable names
    env_var_mapping = {
        "outgoing_email_host": "OUTGOING_EMAIL_HOST",
        "outgoing_email_port": "OUTGOING_EMAIL_PORT",
        "outgoing_email_address": "OUTGOING_EMAIL_ADDRESS",
        "outgoing_email_password": "OUTGOING_EMAIL_PASSWORD",
    }

    # Initialize the config dictionary
    config = {}

    # Check environment variables first
    for key, env_var in env_var_mapping.items():
        value = os.getenv(env_var)
        if value is not None:
            config[key] = value

    # If all required configs are found in environment variables, return the config
    if len(config) == len(env_var_mapping):
        return config

    # If not all configs are found in environment variables, proceed to check files
    possible_paths = []

    if config_file:
        user_provided_path = Path(config_file).expanduser().resolve()
        possible_paths.append(user_provided_path)

    script_dir = Path(__file__).resolve().parent
    package_path = script_dir / ".env.toml"
    possible_paths.append(package_path)

    cwd_path = Path.cwd() / ".env.toml"
    possible_paths.append(cwd_path)

    for config_path in possible_paths:
        if config_path.exists():
            try:
                with config_path.open("rb") as file:
                    file_config = tomllib.load(file)
                    # Update the config dictionary with values from the file
                    for key in env_var_mapping.keys():
                        if key not in config and key in file_config:
                            config[key] = file_config[key]
                # After loading from file, check if all configs are present
                if len(config) == len(env_var_mapping):
                    return config
                else:
                    missing_keys = set(env_var_mapping.keys()) - set(config.keys())
                    logging.error(f"Missing configuration keys: {missing_keys}")
                    raise RuntimeError("Incomplete configuration.")
            except Exception as e:
                logging.error(f"Error loading config file {config_path}: {e}")
                raise RuntimeError("Failed to load configuration file.")

    # If no valid config is found, raise an error
    logging.error(
        f"Config file not found in any of the attempted locations: {possible_paths}"
    )
    raise RuntimeError("Missing configuration file. Check .env.toml location.")


def send_mail(
    subject: str, body: str, recipient: str = None, config_file: str = None
) -> None:
    """Send an email using SMTP settings from a TOML config file.

    Args:
        subject (str): Email subject line.
        body (str): Email message content.
        recipient (str, optional): Recipient email address. Defaults to sender email if not specified.
        config_file (str, optional): Path to the TOML config file. Defaults to `.env.toml` in package directory.
    """
    config = load_config(config_file)

    try:
        # Load email settings from config
        host = config["outgoing_email_host"]
        port = int(config["outgoing_email_port"])
        sender_email = config["outgoing_email_address"]
        sender_password = config["outgoing_email_password"]
        recipient = recipient or sender_email  # Default recipient to sender

        # Create email message
        msg = EmailMessage()
        msg["From"] = sender_email
        msg["To"] = recipient
        msg["Reply-To"] = sender_email
        msg["Subject"] = subject
        msg.set_content(body)

        # Determine SMTP client based on port
        if port == 465:
            smtp_class = smtplib.SMTP_SSL
        elif port == 587:
            smtp_class = smtplib.SMTP
        else:
            logging.warning("Uncommon SMTP port detected. Verify your settings.")
            smtp_class = smtplib.SMTP

        # Send the email using SMTP
        with smtp_class(host, port) as server:
            logging.info(f"Connecting to SMTP server: {host}:{port}")

            if port == 587:  # TLS required for 587
                server.starttls()
                logging.info("TLS started.")

            server.login(sender_email, sender_password)
            logging.info(f"Logged in as {sender_email}. Sending email...")

            server.send_message(msg)
            logging.info("Email sent successfully.")

    except smtplib.SMTPAuthenticationError:
        logging.error("SMTP authentication failed: Invalid username/password.")
        raise RuntimeError("Authentication error: Invalid credentials.")
    except smtplib.SMTPConnectError as e:
        logging.error(f"SMTP connection error: {e}")
        raise RuntimeError(f"SMTP connection error: {e}")
    except smtplib.SMTPException as e:
        logging.error(f"SMTP error occurred: {e}")
        raise RuntimeError(f"SMTP error: {e}")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        raise RuntimeError(f"Unexpected error: {e}")


if __name__ == "__main__":
    logging.info("Starting emailer.py")
    subject_str = "Email from Data Analyst and Python Developer"
    content_str = "Did you know the Python standard library enables emailing?"
    try:
        send_mail(subject=subject_str, body=content_str)
        logging.info("SUCCESS: Email sent.")
    except RuntimeError as e:
        logging.error(f"ERROR: Email sending failed: {e}")

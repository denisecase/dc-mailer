"""
dc_mailer/mailer.py
Send an email with Python and Gmail.
"""

import logging
import smtplib
from email.message import EmailMessage
from dc_mailer.config import load_config

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def get_smtp_client(port: int):
    """Return the appropriate SMTP client class based on the port.

    Args:
        port (int): The port number to check.

    Returns:
        class: The appropriate SMTP client class.
        Returns `smtplib.SMTP_SSL` for port 465
        and `smtplib.SMTP` for port 587 or other ports.
    """
    if port == 465:
        return smtplib.SMTP_SSL  # **Ensure correct SSL handling**
    elif port == 587:
        return smtplib.SMTP
    else:
        logging.warning(f"Uncommon SMTP port {port} detected. Verify your settings.")
        return smtplib.SMTP


def send_mail(
    subject: str, body: str, recipient: str = None, config_file: str = None
) -> None:
    """Send an email using SMTP settings from a TOML config file.

    Args:
        subject (str): Email subject line.
        body (str): Email message content.
        recipient (str, optional): Recipient email address. Defaults to sender email if not specified.
        config_file (str, optional): Path to the TOML config file. Defaults to `.env.toml`.
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

        smtp_class = get_smtp_client(port)

        # Send the email using SMTP
        with smtp_class(host, port) as server:
            logging.info(f"Connecting to SMTP server: {host}:{port}")

            if port == 587:  # TLS required for 587
                server.starttls()
                logging.info("TLS started.")

            server.login(sender_email, sender_password)
            logging.info(f"Logged in as {sender_email}. Sending email...")

            server.send_message(msg)
            logging.info("Email sent.")

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
    logging.info("Ready for work.")
    subject = "Email from Data Analyst and Python Developer"
    body = "Did you know the Python standard library enables emailing?"
    try:
        send_mail(subject=subject, body=body)
        logging.info("SUCCESS: Email sent.")
    except RuntimeError as e:
        logging.error(f"ERROR: Sending failed: {e}")

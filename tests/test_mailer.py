import pytest
from dc_mailer.mailer import send_mail

def test_send_email():
    """Test the send_email function."""
    subject_str = "TEST Email from Data Analyst and Python Developer"
    content_str = "TEST Did you know the Python standard library enables emailing?"
    
    try:
        send_mail(subject=subject_str, body=content_str, recipient="someone@example.com")
    except Exception as e:
        pytest.fail(f"send_email() raised an exception: {e}")

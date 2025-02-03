# This file makes this folder an importable package.

# Import the function from Python file in the same directory
from .mailer import send_mail

# Define what is available when using from this import *
__all__ = ["send_mail"]

# This file makes `dc_emailer/` an importable package.

# Import the function from `emailer.py` in the same directory
from .emailer import send_email

# Define what is available when using "from dc_emailer import *"
__all__ = ["send_email"]

# email-alert

> Send an email alert using Python

## Requirements

- Python 3.11+ (required for reading toml files)
- A configured Gmail Account (see below)
---

## Step 1. Install this Module

Add this to your requirements.txt and install. 

```
git+https://github.com/denisecase/email-alert.git
```

## Step 2. Add .env.toml To your Python Project

Create a new .env.toml file in your Python project (or add these entries).
Update the outgoing email address to your gmail address.
We'll create a password below.  

```
outgoing_email_host = "smtp.gmail.com"
outgoing_email_port = 587
outgoing_email_address = "your-email@gmail.com"
outgoing_email_password = "your-app-password"
```

## Step 3. Add .env.toml To .gitignore

Ensure your secrets are not published by adding an entry in .gitignore:

```
.env.toml
```

## Step 4. Gmail - Enable IMAP

 - Open Gmail.
 - Click Settings or ⚙️ in the top-right.
 - Then click "See all settings".
 - Navigate to "Forwarding and POP/IMAP".
 - Under "IMAP access", select "Enable IMAP".
-  Click "Save Changes".

## Step 5. Gmail - Generate an App Password

If your account has 2FA enabled, you must generate an App Password:
- Go to <https://support.google.com/accounts/answer/185833?hl=en> 
- Sign in and navigate to Account "Security" / "App Passwords"
- Create an app password - name it (e.g., "PythonEmailAlerts"). 
- Generate and copy the 16-character password.
- Paste the 16-char as your password in .env.toml file. 
  - Remove any spaces
  - Keep it private - ensure your .env.toml file is listed in .gitignore

## Step 6. Import and Use in a Python Script

Once installed and your .env.toml file is ready, you can use it in your code. 

```python
from utils_email.emailer import send_mail

# Define email details
title = "Email from Data Analyst and Python Developer"
content = "Did you know the Python standard library enables emailing?"
recipient = "your.email@gmail.com"

# Send email
try:
    send_email(subject=title, body=content, recipient=recipient)
    print("SUCCESS: Email sent successfully.")
except RuntimeError as e:
    print(f"ERROR: Email sending failed: {e}")
```
---

## Testing

To run this file locally for testing, fork & clone the repo, add .env.toml. 
Open the project repository in VS Code, open a PowerShell terminal and run 

```
pytest
py email_alert\emailer.py
```

## A Note on Organization

Repository Name: email-alert
  - Uses dashes (-) as allowed in GitHub repository names.
  - Cannot be used as a Python package name.

Package (Folder) Name: email_alert
  - Uses underscores (_) to ensure compatibility with Python imports.
  - Becomes a package by including an __init__.py file.

Module Name: emailer.py
  - The file name with a .py extension.
  - Can be executed as a script or imported as a module.

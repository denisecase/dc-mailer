# dc-mailer

> Send an email alert using Python and Gmail

## Requirements

- Python 3.11+ (required for reading toml files)
- A configured Gmail Account (see below)
---

## Step 1. Install this Module

Use `pip install dc-mailer`
or add `dc-mailer` to your requirements.txt and install. 

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

Ensure your secrets are not published with an entry in .gitignore:

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
- Click on "Create and manage your app passwords".
- Sign in and navigate to Account "Security" / "App Passwords"
- Create an app password - name it (e.g., "PythonEmailAlerts"). 
- Generate and copy the 16-character password.
- Paste the 16-char as your password in .env.toml file. 
  - Remove any spaces
  - Keep it private - ensure your .env.toml file is listed in .gitignore

## Step 6. Import and Use in a Python Script

Once installed and your .env.toml file is ready, you can use it in your code. 

```python
from dc_mailer import send_mail

title = "Email from Data Analyst and Python Developer"
content = "Did you know the Python standard library enables emailing?"
recipient = "your.email@gmail.com"

try:
    send_mail(subject=title, body=content, recipient=recipient)
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
py dc_mailer\mailer.py
```

# mail_generator.py

import smtplib
from email.message import EmailMessage
from message_schema import CanonicalMessage
from typing import Optional
import os # To read environment variables for SMTP credentials

# --- SMTP Configuration ---
# IMPORTANT: You'll need to use a real mail server (e.g., Gmail with App Password, SendGrid, etc.)
# For the MVP, we'll use environment variables for security.
SMTP_SERVER = os.environ.get("SMTP_SERVER", "smtp.example.com") 
SMTP_PORT = int(os.environ.get("SMTP_PORT", 587))
SMTP_USERNAME = os.environ.get("SMTP_USERNAME", "your_smtp_user") 
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "your_smtp_password")
SENDER_NAME = "Structured Communication Gateway"

# mail_generator.py (add to existing content)

def create_email_body(message: CanonicalMessage) -> str:
    """Generates the clean, structured text body for the email recipient."""
    
    # 1. Structured Header (The key for quick filtering)
    header = (
        f"--- Structured Message Summary ---\n"
        f"Intent Tag: {message.intent_tag}\n"
        f"Internal Tag: {message.internal_tag if message.internal_tag else 'N/A'}\n"
        f"Timestamp: {message.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
        f"Sent Via: {SENDER_NAME}\n"
        f"---------------------------------\n\n"
    )
    
    # 2. Main Content
    body = f"Message Body:\n{message.body_content}\n"
    
    # 3. Footer (Optional, for branding or app info)
    footer = (
        f"\n\n--\n"
        f"This structured message was sent using the [Your App Name] Gateway."
    )
    
    return header + body + footer

# mail_generator.py (add to existing content)

def send_structured_email(message: CanonicalMessage) -> bool:
    """
    Constructs and sends the email based on the CanonicalMessage.
    Returns True on success, False otherwise.
    """
    try:
        # 1. Create the email message object
        msg = EmailMessage()
        
        # Inject the key Intent Tag directly into the subject line
        formatted_subject = f"[{message.intent_tag}] {message.subject}"
        
        msg['Subject'] = formatted_subject
        msg['From'] = f"{SENDER_NAME} <{message.sender_email}>"
        msg['To'] = message.recipient_email
        
        # 2. Generate the body content
        email_body = create_email_body(message)
        msg.set_content(email_body)

        # 3. Connect to the SMTP Server (securely)
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls() # Secure the connection
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
        
        print(f"SUCCESS: Message {message.message_id} sent to {message.recipient_email}")
        return True
        
    except Exception as e:
        print(f"ERROR sending message {message.message_id}: {e}")
        return False

import smtplib
import ssl
from dotenv import load_dotenv
import os

def send_email(subject, body, receiver_email):
    # Load environment variables from .env file
    load_dotenv()

    # Retrieve SMTP settings from environment variables
    smtp_server = os.getenv("SMTP_SERVER")
    port = int(os.getenv("SMTP_PORT"))
    smtp_username = os.getenv("SMTP_USERNAME")
    smtp_password = os.getenv("SMTP_PASSWORD")
    sender_email = os.getenv("SENDER_EMAIL")  # You can set this in the .env file
    receiver_email = os.getenv("RECEIVER_EMAIL")

    message = f"""\
Subject: {subject}

{body}
"""
    context = ssl.create_default_context()

    try:
        with smtplib.SMTP(smtp_server, port) as server:
            server.starttls(context=context)  # Secure the connection
            server.login(smtp_username, smtp_password)
            server.sendmail(sender_email, receiver_email, message)
            print("Email sent successfully!")
            return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False
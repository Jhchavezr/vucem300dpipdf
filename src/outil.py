
import smtplib
import ssl
from dotenv import load_dotenv
import os
from email.mime.text import MIMEText



def send_email(subject, body):
    # Load environment variables from .env file
    load_dotenv()

    # Retrieve SMTP settings from environment variables
    smtp_server = os.getenv("SMTP_SERVER")
    port = int(os.getenv("SMTP_PORT"))
    smtp_username = os.getenv("SMTP_USERNAME")
    smtp_password = os.getenv("SMTP_PASSWORD")
    sender_email = os.getenv("SENDER_EMAIL")  # You can set this in the .env file
    receiver_email = os.getenv("RECEIVER_EMAIL")

    body = f"""\
    From: {sender_email}
    To: {receiver_email}
    Subject: {subject}

    {body}
    """
    
    try:
        # Prepare the email
        msg = MIMEText(body)
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = subject

        # Establish connection and use STARTTLS
        server = smtplib.SMTP(smtp_server, port)  # Use SMTP, not SMTP_SSL
        server.ehlo()  # Can be omitted; it's optional, but good practice
        server.starttls()  # Upgrade the connection to SSL/TLS
        server.ehlo()  # Can be omitted; it's optional, but good practice
        server.login(smtp_username, smtp_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()

        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")
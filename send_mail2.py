import smtplib
import os
from email.mime.text import MIMEText

# SMTP settings
smtp_server = "smtp.titan.email"  # Use the correct SMTP server
port = 587  # Port for STARTTLS
smtp_username = "webmaster@marchainternacional.com"
smtp_password = "Jhchavezr1!"

# Email details
sender_email = "webmaster@marchainternacional.com"
receiver_email = "serviciosole@gmail.com"
subject = "Test Email from Hostgator"
body = "This is a test email sent from Python using Hostgator. MIME"

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

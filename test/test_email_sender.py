import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# SMTP server configuration
smtp_server = 'localhost'
smtp_port = 1025

# Email details
sender_email = 'sender@example.com'
recipient_email = 'recipient@example.com'
subject = 'Test Email'
body = 'This is a test email sent to aiosmtpd server.'

# Create a MIMEText object to represent the email
msg = MIMEMultipart()
msg['From'] = sender_email
msg['To'] = recipient_email
msg['Subject'] = subject

# Attach the email body to the MIMEText object
msg.attach(MIMEText(body, 'plain'))

# Send the email
try:
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.sendmail(sender_email, recipient_email, msg.as_string())
        print(f"Email sent successfully to {recipient_email}")
except Exception as e:
    print(f"Failed to send email: {e}")

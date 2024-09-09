import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_email(subject, body, recipient):
    # SMTP configuration from environment variables
    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")
    sender_email = os.getenv("SENDER_EMAIL")

    # Create message
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    # Send email
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Enable TLS
        server.login(smtp_user, smtp_password)
        server.sendmail(sender_email, recipient, msg.as_string())
        server.quit()
        print(f"Email sent to {recipient}")
    except Exception as e:
        print(f"Failed to send email: {str(e)}")


if __name__ == "__main__":
    # Example usage

    ## Get a list of eligible users to send a reminder email to. Ignore the ones deactivated
    ## and remove them from the file

    deactivation_candidates = []
    ## For each user determine how many reminders have been sent
    reminders_by_candidate = {}

    ## If reminders less than 2 send email
    email_candidates =[]
    for recipient in email_candidates:
        recipient = os.getenv("EMAIL_RECIPIENT")
        subject = "Your Subject Here"
        body = "This is the body of the email."
        send_email(subject, body, recipient)

    #Deactivate the users using the endpoint
    for user in deactivation_candidates:
        #Deactivate users by ca
        pass

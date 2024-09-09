import os
import json
import requests
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import argparse

DOMINO_EXTENSIONS_API_SVC = "domino-extensions-api-svc"


# FIND ALL INACTIVE USERS (1)
def get_token():
    # Fetch the mounted service account token
    uri = os.environ['DOMINO_API_PROXY']
    return requests.get(f"{uri}/access-token").text


def get_inactive_users(no_of_days, include_svc_accounts=False):
    dns_name = f"{DOMINO_EXTENSIONS_API_SVC}.domino-field.svc.cluster.local"
    endpoint = f"user-management/inactivefor/{no_of_days}"
    url = f"http://{dns_name}/{endpoint}"
    payload = {"users": ['user-ds-1', 'user-ds-2']}
    token = get_token()
    my_headers = {"Authorization": f"Bearer {token}", 'Content-Type': 'application/json'}
    domino_api_host = os.environ['DOMINO_API_HOST']
    r = requests.get(url, headers=my_headers)
    lst = r.json()['inactive_accounts']
    new_lst = []
    for l in lst:
        if not l['is_svc_account']:
            new_lst.append(l)
    return new_lst


def deactivate_users(users):
    service_name = "domino-extensions-api-svc"
    dns_name = f"{DOMINO_EXTENSIONS_API_SVC}.domino-field.svc.cluster.local"
    endpoint = "user-management/deactivate"
    url = f"http://{dns_name}/{endpoint}"
    payload = {"users": users}
    token = get_token()
    my_headers = {"Authorization": f"Bearer {token}", 'Content-Type': 'application/json'}
    r = requests.post(url, headers=my_headers, json=payload)
    return r.json()


def get_email_tracker_file_name(dataset_name):
    return f"/domino/datasets/local/{dataset_name}/email_tracker.json"


def get_email_tracker(dataset_name):
    # Define the path to the JSON file
    json_file_path = get_email_tracker_file_name(dataset_name)

    # Check if the file exists
    if not os.path.exists(json_file_path):
        # If the file does not exist, create an empty JSON file
        with open(json_file_path, 'w') as file:
            json.dump({}, file)  # Create an empty JSON object (empty dictionary)
    with open(json_file_path, 'r') as file:
        data = json.load(file)
    return data


def get_emails_by_user():
    domino_api_host = os.environ['DOMINO_API_HOST']
    url = f"{domino_api_host}/api/users/v1/users"
    token = get_token()
    my_headers = {"Authorization": f"Bearer {token}", 'Content-Type': 'application/json'}
    out = requests.get(url, headers=my_headers)
    users = out.json()['users']
    email_by_user_name = {}
    for u in users:
        email_by_user_name[u['userName']] = u['email']
    return email_by_user_name


# SEND EMAIL TO USERS TO WHOM LESS THAN MAX_EMAILS_BEFORE_USER_DELETED HAVE BEEN SENT
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
        if smtp_password:
            server.starttls()  # Enable TLS
            server.login(smtp_user, smtp_password)
        server.sendmail(sender_email, recipient, msg.as_string())
        server.quit()
        print(f"Email sent to {recipient}")
        return True
    except Exception as e:
        print(f"Failed to send email: {str(e)}")
        return False


def main(idle_duration_threshold, max_emails_before_user_deleted, dataset_name, deactivate_users_flag):
    # GET INACTIVE USERS TO WHOM EMAILS HAVE BEEN SENT OUT
    email_status_by_user = get_email_tracker(dataset_name)

    # Get Inactive Users
    inactive_user_list = get_inactive_users(idle_duration_threshold)
    print('Inactive User List')
    print(inactive_user_list)

    # DELETE USERS FROM THIS LIST WHAT ARE NOT IN THE INACTIVE LIST JUST FETCHED (1)
    users = email_status_by_user.keys()
    current_inactive_user_names = [user['user_name'] for user in inactive_user_list]
    # print(current_inactive_user_names)

    update_email_status_by_user = {}
    for user in current_inactive_user_names:
        if user in email_status_by_user.keys():
            update_email_status_by_user[user] = email_status_by_user[user]
        else:
            update_email_status_by_user[user] = 0
    print('Email Reminder Status By Inactive Users')
    print(update_email_status_by_user)

    # IDENTIFY USERS TO WHOM EMAIL NEEDS TO BE SENT OUT
    email_reminder_candiates = {}
    for user, email_reminder_count in update_email_status_by_user.items():
        if email_reminder_count < max_emails_before_user_deleted:
            email_reminder_candiates[user] = email_reminder_count

    # IDENTIFY USERS TO BE DEACTIVATED
    users_to_deactivate = []
    for user, email_reminder_count in update_email_status_by_user.items():
        if email_reminder_count >= max_emails_before_user_deleted:
            users_to_deactivate.append(user)

    print("Candidates for Email Reminders")
    print(email_reminder_candiates)
    print("Candidates for Deactivation")
    print(users_to_deactivate)

    emails_by_user = get_emails_by_user()

    new_user_counts = {}
    for user, count in email_reminder_candiates.items():
        new_count = count + 1
        body = f"You have not logged in for {idle_duration_threshold} days. Your account will be deactivated"
        result = send_email(f"Email Deactivation Reminder {new_count}", body, emails_by_user[user])
        email_reminder_candiates[user] = new_count

    # Update the file
    json_file_path = get_email_tracker_file_name(dataset_name)
    with open(json_file_path, 'w') as file:
        json.dump(email_reminder_candiates, file)
    print(email_reminder_candiates)
    deactivated_users = deactivate_users(users_to_deactivate)
    if deactivate_users_flag:
        print("Deactivated Users")
        print(deactivated_users)
    else:
        print("Deactivated Users Flag set to False, skipping the users below")
        print(deactivated_users)


if __name__ == "__main__":
    # Create the argument parser
    parser = argparse.ArgumentParser(
        description="Three Arguments IDLE_DURATION_THRESHOLD_IN_DAYS,MAX_EMAILS_BEFORE_USER_DELETED,DATASET_NAME ")

    # Add a string argument
    parser.add_argument('idle_duration_threshold', type=int, help="The number of days the user has been active")

    # Add an integer argument
    parser.add_argument('max_emails_before_user_deleted', type=int,
                        help="The number of email reminders before user deactivated")

    parser.add_argument('dataset_name', type=str,
                        help="The name of the dataset where the user reminder count is stored")

    parser.add_argument('--deactivate_users_flag', action='store_true', help="If specified, users will be deactivated")
    # Parse the arguments
    args = parser.parse_args()

    # Call the main function with parsed arguments
    main(args.idle_duration_threshold, args.max_emails_before_user_deleted, args.dataset_name,
         args.deactivate_users_flag)
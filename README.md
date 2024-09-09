# Auto Deactivation of Users with Email Reminders

This repo can be used to deactivate users who have been inactive for a fixed duration of time.

Features included are-

1. Send email reminders to users that their account is going to be deactivated
2. After a pre-defined number of reminders, if the user has still not logged into Domino
   deactivate the user automatically


## Pre-requisites

Install the [Domino Extensions API](https://github.com/dominodatalab/domino-field-solutions-installations/blob/main/domino-extensions-api/README.md).

## How use this repo

Follow the steps below:

### Configure your SMTP Server Connectivity from inside the Domino Job 

You need to have an SMTP server running. To start one locally inside the job run the command below

```shell
 python3 -m aiosmtpd -n -l localhost:1025
```

If using a local SMTP server make sure to configure the following user environment variables

```shell
export SMTP_SERVER=localhost
export SMTP_PORT=1025
export SMTP_USER=fake-admin
export SMTP_PASSWORD=""
export SENDER_EMAIL=domino-deactivator@test.com
```
If you are using an externallly configured SMTP server, update the environment variables
using your own values.


Run the notebook `email_sender.ipynb`

### Identify the dataset which will be used to track email reminders

As an example I have created and used a dataset called - `EmailRemindersUserDeactivation`

This dataset will contain a file called `/domino/datasets/local/{dataset_name}/email_tracker.json`
which will track the number of email reminders sent to each user. If a user logs in after a reminder
but before a deactivation, the entry is removed from this file when this process runs again the next time


### Create a Job which sends emails and deactivates users

Setup the call to `deactivation.sh` as a Scheduled Job. Open the file and notice the parameters used to execute the job
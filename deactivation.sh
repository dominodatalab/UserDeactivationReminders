EXPORT NO_OF_DAYS_INACTIVE = 5
EXPORT NO_OF_REMINDERS_BEFORE_DEACTIVATION = 2
EXPORT DATASET_NAME=EmailRemindersUserDeactivation


python3 email_sender.py $NO_OF_DAYS_INACTIVE $NO_OF_REMINDERS_BEFORE_DEACTIVATION $DATASET_NAME --deactivate_users_flag

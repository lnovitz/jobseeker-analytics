import os.path
import base64

from bs4 import BeautifulSoup
import re


from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from constants import QUERY_APPLIED_EMAIL_FILTER
from db_utils import write_emails
from email_utils import (
    clean_email,
    get_word_frequency,
    get_gmail_credentials,
    get_message,
    get_company_name,
    get_received_at_timestamp,
    get_email_subject_line,
    get_email_domain_from_address,
    get_email_from_address,
)
import datetime


JOBS_LABEL_ID = "Label_7646018251861665561"
# ideally would be able to programmatically fetch job application-related emails but in interest of time,
# I manually filtered and placed in this label 'jobs' with this id starting with Label_


def main():
    creds = get_gmail_credentials()
    try:
        # Call the Gmail API
        service = build("gmail", "v1", credentials=creds)
        # results = service.users().labels().list(userId="me").execute()
        # labels = results.get("labels", [])
        results = (
            service.users()
            .messages()
            .list(userId="me", q=QUERY_APPLIED_EMAIL_FILTER, includeSpamTrash=True)
            .execute()
        )

        messages = results.get("messages", [])
        next_page_token = results.get("nextPageToken", "")
        size_estimate = results.get("resultSizeEstimate", 0)
        print("next page token {}".format(next_page_token))
        print("size estimate {}".format(size_estimate))
        # print(results)
        if not results:
            print("No message found.")
            return

        # Directory to save the emails
        output_dir = "emails_v2"
        os.makedirs(output_dir, exist_ok=True)
        emails_data = []
        i = 0
        for message in messages:
            message_data = {}
            # (email_subject, email_from, email_domain, company_name, email_dt)
            msg_id = message["id"]
            msg = get_message(id=msg_id, gmail_instance=service)

            # Constructing the object which will be written into db
            message_data["subject"] = [get_email_subject_line(msg)]
            message_data["from_name"] = [get_email_from_address(msg)]
            message_data["fromdomain_match"] = [
                get_email_domain_from_address(message_data["from_name"][i])
            ]
            message_data["top_word_company_proxy"] = [get_company_name(msg)]
            message_data["received_at"] = [get_received_at_timestamp(msg_id, msg)]

            filename = f"{msg_id}.txt"  # or use ".json" and change content accordingly
            filepath = os.path.join(output_dir, filename)
            print(f"Saved email {msg_id} to {filepath}")

            emails_data.append(message_data)
            i += 1
            break

        cleaned_emails = []
        for email_dict in emails_data:
            cleaned_email = []
            for key in email_dict:
                cleaned_email.append(email_dict[key][0])
                continue  # not sure this is necessary? What is this?
            cleaned_emails.append(tuple(cleaned_email))
        write_emails(cleaned_emails)
    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f"An error occurred: {error}")


if __name__ == "__main__":
    main()

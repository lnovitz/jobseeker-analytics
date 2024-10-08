import os.path
import base64
import spacy
from spacy_cleaner import processing, Cleaner

from bs4 import BeautifulSoup
import re

from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from db_utils import write_emails
import datetime

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

JOBS_LABEL_ID = "Label_7646018251861665561"
# ideally would be able to programmatically fetch job application-related emails but in interest of time,
# I manually filtered and placed in this label 'jobs' with this id starting with Label_


def get_gmail_credentials():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except RefreshError:
                os.remove("token.json")
                creds.refresh(Request())
        else:
            try:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json",
                    scopes=SCOPES,
                )
                creds = flow.run_local_server(port=8001)
            except RefreshError:
                os.remove("token.json")
                creds.refresh(Request())
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return creds


def clean_email(email_body):
    model = spacy.load("en_core_web_sm")
    pipeline = Cleaner(
        model,
        processing.remove_stopword_token,
        processing.remove_punctuation_token,
        processing.remove_number_token,
    )
    return pipeline.clean([email_body])


def get_word_frequency(cleaned_email):
    word_dict = {}
    for word in cleaned_email[0].split(" "):
        if word not in word_dict:
            word_dict[word] = 1
        else:
            word_dict[word] += 1

    word_dict_sorted = sorted(word_dict.items(), key=lambda item: item[1], reverse=True)
    return word_dict_sorted


def main():
    creds = get_gmail_credentials()
    try:
        # Call the Gmail API
        service = build("gmail", "v1", credentials=creds)
        # results = service.users().labels().list(userId="me").execute()
        # labels = results.get("labels", [])
        query = (
            '(subject:"thank" AND from:"no-reply@ashbyhq.com") OR '
            '(subject:"thank" AND from:"careers@") OR '
            '(subject:"thank" AND from:"no-reply@greenhouse.io") OR '
            '(subject:"application was sent" AND from:"jobs-noreply@linkedin.com") OR '
            'from:"notification@smartrecruiters.com" OR '
            'subject:"application received" OR '
            'subject:"received your application" OR '
            'subject:"your application to" OR '
            'subject:"applied to" OR '
            'subject:"your application was sent to" OR '
            'subject:"thank you for your submission" OR '
            'subject:"thank you for applying" OR '
            'subject:"thanks for applying to" OR '
            'subject:"confirmation of your application" OR '
            'subject:"your recent job application" OR '
            'subject:"successfully submitted" OR '
            'subject:"application received" OR '
            'subject:"application submitted" OR '
            'subject:"we received your application" OR '
            'subject:"thank you for your submission" OR '
            'subject:"thank you for your interest" OR '
            'subject:"thanks for your interest" OR '
            'subject:"thank you for your application" OR '
            'subject:"thank you from" OR '
            'subject:"application has been submitted" OR '
            '(subject:"application to" AND subject:"successfully submitted") OR '
            '(subject:"your application to" AND subject:"has been received") OR '
            '(subject:"your application for" AND -subject:"update") OR '
            'subject:"your job application has been received" OR '
            'subject:"thanks for your application" OR '
            'subject:"job application confirmation" OR '
            'subject:"ve been referred" OR '
            '(subject:"we received your" AND subject:"application")'
        )  # label:jobs -label:query4
        results = (
            service.users()
            .messages()
            .list(userId="me", q=query, includeSpamTrash=True)
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
        for message in messages:
            message_data = {}
            # (email_subject, email_from, email_domain, company_name, email_dt)
            msg_id = message["id"]
            # if msg_id == "1901318a60244309":
            #     import pdb

            #     pdb.set_trace()
            # else:
            #     continue

            msg = service.users().messages().get(userId="me", id=msg_id).execute()
            email_data = msg["payload"]["headers"]

            for values in email_data:
                name = values["name"]
                if name == "From":
                    from_name = values["value"]
                    print(from_name)
                    subject = [j["value"] for j in email_data if j["name"] == "Subject"]
                    print(subject)
                    if message_data.get("subject"):
                        message_data["subject"].append(subject)
                    else:
                        message_data["subject"] = [subject]
                    if message_data.get("from_name"):
                        message_data["from_name"].append(from_name)
                    else:
                        message_data["from_name"] = [from_name]
                if name == "ARC-Authentication-Results":
                    print("yes ARC")
                    arc_authentication_results = values["value"]
                    fromdomain_pattern = r"from=([\w.-]+)"
                    fromdomain_matches = re.findall(
                        fromdomain_pattern, arc_authentication_results
                    )
                    fromdomain_match = (
                        fromdomain_matches[0] if fromdomain_matches else ""
                    )
                    if message_data.get("fromdomain_match"):
                        message_data["fromdomain_match"].append(fromdomain_match)
                    else:
                        message_data["fromdomain_match"] = [fromdomain_match]

            payload = msg.get("payload")
            if payload:
                payload_parts = payload.get("parts")
                if payload_parts:
                    for p in payload_parts:
                        if p["mimeType"] in ["text/plain", "text/html"]:
                            data = base64.urlsafe_b64decode(
                                p.get("body", {}).get("data", {})
                            ).decode("utf-8")
                            # Parse the content with BeautifulSoup
                            soup = BeautifulSoup(data, "html.parser")

                            # Extract the plain text from the HTML content
                            email_text = soup.get_text()
                            cleaned_text = clean_email(email_text)

                            if cleaned_text:
                                word_frequency = get_word_frequency(cleaned_text)
                                print(word_frequency)
                                top_word_company_proxy = word_frequency[0][0]
                                if message_data.get("top_word_company_proxy"):
                                    message_data["top_word_company_proxy"].append(
                                        top_word_company_proxy
                                    )
                                else:
                                    message_data["top_word_company_proxy"] = [
                                        top_word_company_proxy
                                    ]
                                filename = f"{msg_id}.txt"  # or use ".json" and change content accordingly
                                filepath = os.path.join(output_dir, filename)

                                print(f"Saved email {msg_id} to {filepath}")

                else:
                    # '18fe32d9f3325ccb', '18fe57a5ea4b9650', '190093da22ff5e29'
                    print(
                        "this payload doesnt have parts for message {id}".format(
                            id=msg_id
                        )
                    )
            message_data["received_at"] = [datetime.datetime.now()]
            emails_data.append(message_data)
            break
        cleaned_emails = []
        for email_dict in emails_data:
            cleaned_email = []
            for key in email_dict:
                cleaned_email.append(email_dict[key][0])
                continue
            cleaned_emails.append(tuple(cleaned_email))
        write_emails(cleaned_emails)
    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f"An error occurred: {error}")


if __name__ == "__main__":
    main()

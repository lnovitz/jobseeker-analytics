"""
This file contains the main constants used in the application.
"""
import os
import json

SCOPES = json.loads(os.getenv("GOOGLE_SCOPES").strip("'\""))
CLIENT_SECRETS_FILE = "credentials.json"
REDIRECT_URI = os.getenv("REDIRECT_URI")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
COOKIE_SECRET = os.getenv("COOKIE_SECRET")

QUERY_APPLIED_EMAIL_FILTER = (
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

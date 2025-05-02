import base64
import email
import logging
import re
from typing import Dict, Any

from bs4 import BeautifulSoup
from email_validator import validate_email, EmailNotValidError

from constants import GENERIC_ATS_DOMAINS

logger = logging.getLogger(__name__)


def clean_whitespace(text: str) -> str:
    """
    remove \n, \r, and \t from strings
    """
    return text.replace("\n", "").replace("\r", "").replace("\t", "")


def is_automated_email(email: str) -> bool:
    """
    Determines if an email address is automated or from a person.

    Parameters:
    email (str): The email address to classify.

    Returns:
    bool: True if automated, False otherwise.
    """
    # Define patterns for common automated prefixes and domains
    automated_patterns = [
        r"^no[-_.]?reply@",  # Matches "no-reply", "no_reply", "noreply"
        r"^do[-_.]?not[-_.]?reply@",  # Matches "do-not-reply", "do_not_reply"
        r"^notifications@",  # Matches "notifications@"
        r"^team@",  # Matches "team@"
        r"^hello@",  # Matches "hello@" (often automated)
        r"@smartrecruiters\.com$",  # Matches specific automated domains
    ]

    # Check against the patterns
    for pattern in automated_patterns:
        if re.search(pattern, email, re.IGNORECASE):
            return True  # It's an automated email

    return False  # It's likely from a person


def is_valid_email(email: str) -> bool:
    try:
        validate_email(email)
        return True
    except EmailNotValidError as e:
        # email is not valid, exception message is human-readable
        print(str(e))
        return False


def get_email_content(email_data: Dict[str, Any]) -> str:
    """
    parses html content of email data and appends it to text content and subject conent

    Note 1: linkedIn easy apply messages have *different* html and text_content, so we need to keep both
    Note 2: some automated emails only contain the information about the company in the subject and
        not the email body, so we need to append this to make sure the email processor gets to see it.

    """
    text_content = email_data["subject"]

    if email_data["text_content"]:
        text_content += "\n"
        text_content += email_data["text_content"]

    if email_data["html_content"]:
        soup = BeautifulSoup(email_data["html_content"], "html.parser")
        html_content = soup.get_text(separator=" ", strip=True)

        text_content += "\n"
        text_content += html_content

    return text_content


def get_email(message_id: str, gmail_instance=None):
    if gmail_instance:
        try:
            message = (
                gmail_instance.users()
                .messages()
                .get(userId="me", id=message_id, format="raw")
                .execute()
            )
            msg_str = base64.urlsafe_b64decode(message["raw"].encode("ASCII")).decode(
                "utf-8"
            )
            mime_msg = email.message_from_string(msg_str)
            # logger.info("mime_msg: %s", mime_msg)
            # logger.info("msg_str: %s", msg_str)
            email_data = {
                "id": message_id,
                "threadId": message.get("threadId", None),
                "from": None,
                "to": None,
                "subject": None,
                "date": None,
                "text_content": None,
                "html_content": None,
            }

            # Getting email headers
            email_data["from"] = clean_whitespace(mime_msg.get("From"))
            email_data["to"] = clean_whitespace(mime_msg.get("To"))
            email_data["subject"] = clean_whitespace(mime_msg.get("Subject"))
            email_data["date"] = mime_msg.get("Date")

            # Extract body of the email
            if mime_msg.is_multipart():
                for part in mime_msg.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition"))
                    if (
                        content_type == "text/plain"
                        and "attachment" not in content_disposition
                    ):
                        raw_content = part.get_payload(
                            decode=True
                        ).decode(encoding="utf-8", errors="ignore")
                        email_data["text_content"] = clean_utf8(raw_content)
                    elif (
                        content_type == "text/html"
                        and "attachment" not in content_disposition
                    ):
                        email_data["html_content"] = part.get_payload(
                            decode=True
                        ).decode(encoding="utf-8", errors="ignore")
            else:
                content_type = mime_msg.get_content_type()
                if content_type == "text/plain":
                    raw_content = mime_msg.get_payload(
                        decode=True
                    ).decode(encoding="utf-8", errors="ignore")
                    email_data["text_content"] = clean_utf8(raw_content)
                elif content_type == "text/html":
                    email_data["html_content"] = mime_msg.get_payload(
                        decode=True
                    ).decode(encoding="utf-8", errors="ignore")

            email_data["raw_text_content"] = email_data["text_content"]
            email_data["text_content"] = get_email_content(email_data)

            return email_data

        except Exception as e:
            logger.exception(f"Error retrieving email with id {message_id}: {e}")
            return {}
    return {}


def get_email_ids(query: tuple = None, gmail_instance=None):
    # email_ids = []
    thread_latest_messages = {}
    page_token = None

    while True:
        response = (
            gmail_instance.users()
            .messages()
            .list(
                userId="me",
                q=query,
                includeSpamTrash=True,
                pageToken=page_token,
            )
            .execute()
        )

        if "messages" in response:
            # Process each message
            for message in response["messages"]:
                message_id = message["id"]
                thread_id = message["threadId"]
                
                # Get the full message to access internal date
                msg_detail = gmail_instance.users().messages().get(
                    userId="me", 
                    id=message_id, 
                    format="metadata",
                    metadataHeaders=["Date"]
                ).execute()
                
                # Internal date is in milliseconds since epoch
                internal_date = int(msg_detail.get("internalDate", 0))
                
                # If this thread hasn't been seen before, or if this message is newer
                if thread_id not in thread_latest_messages or internal_date > thread_latest_messages[thread_id]["date"]:
                    thread_latest_messages[thread_id] = {
                        "id": message_id,
                        "date": internal_date
                    }

        page_token = response.get("nextPageToken")
        if not page_token:
            break

    # return email_ids
    latest_message_ids = [msg_info["id"] for msg_info in thread_latest_messages.values()]
    return latest_message_ids


def get_email_payload(msg):
    return msg.get("payload", None)


def get_email_headers(msg):
    email_data = get_email_payload(msg)
    if email_data:
        return email_data.get("headers", None)
    return None


def get_email_parts(msg):
    email_data = get_email_payload(msg)
    if email_data:
        return email_data.get("parts", None)
    return None


def get_email_subject_line(msg):
    try:
        email_headers = get_email_headers(msg)
        if email_headers:
            for header in email_headers:
                key = header.get("name")
                if key == "Subject":
                    return header.get("value", "")
    except Exception as e:
        logger.error("Error getting email subject line: %s", e)
    return ""


def get_last_capitalized_words_in_line(line):
    try:
        words = line.split()
        last_capitalized_words = []
        for word in reversed(words):
            if word[0].isupper():
                last_capitalized_words.append(word)
            else:
                break
        return " ".join(reversed(last_capitalized_words))
    except Exception as e:
        logger.error("Error getting last capitalized words in email subject: %s", e)
    return ""


def get_email_from_address(msg):
    try:
        email_headers = get_email_headers(msg)
        if email_headers:
            for header in email_headers:
                if header.get("name") == "From":
                    # if value enclosed in <> then extract email address
                    # else return the value as is
                    from_address = header.get("value")
                    if "<" in from_address:
                        return from_address.split("<")[1].split(">")[0]
                    return from_address
    except Exception as e:
        logger.error("Error getting email from address: %s", e)
    return ""


def get_received_at_timestamp(message_id, msg):
    import datetime

    try:
        email_headers = get_email_headers(msg)
        if email_headers:
            for header in email_headers:
                key = header.get("name")
                if key == "Date":
                    return header.get("value")
    except Exception as e:
        print("msg_%s: %s" % (message_id, e))
    return datetime.datetime.now()  # default if trouble parsing


def is_generic_email_domain(domain):
    # input expects return value of get_email_domain_from_address
    return domain in GENERIC_ATS_DOMAINS


def get_email_domain_from_address(email_address):
    return email_address.split("@")[1] if "@" in email_address else ""


def clean_utf8(text: str, mode: str = 'basic') -> str:
    """
    Clean text by removing or replacing problematic UTF-8 characters.
    
    Args:
        text (str): The text to clean
        mode (str): Cleaning level - 'basic', 'moderate', or 'aggressive'
        
    Returns:
        str: Cleaned text
    """
    import re
    import unicodedata
    
    if not text:
        return text
    
    # Basic cleaning - remove control characters and zero-width characters
    if mode == 'basic':
        # Remove control characters
        text = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', text)
        # Remove zero-width characters
        text = re.sub(r'[\u200B-\u200D\uFEFF]', '', text)
    
    # Moderate cleaning - normalize and remove emojis and most symbols
    elif mode == 'moderate':
        # Normalize unicode characters (convert to canonical form)
        text = unicodedata.normalize('NFKD', text)
        # Remove emojis and symbols
        text = re.sub(r'[^\u0000-\u007F\u0080-\u00FF\u0100-\u017F\u0180-\u024F\u0250-\u02AF\u0300-\u036F]', '', text)
    
    # Aggressive cleaning - ASCII only
    elif mode == 'aggressive':
        # Keep only ASCII characters
        text = re.sub(r'[^\x00-\x7F]', '', text)
    
    # Remove any resulting double spaces
    text = re.sub(r' {2,}', ' ', text)
    return text


def remove_email_addresses(text: str, replacement: str = "[EMAIL]") -> str:
    """
    Remove all email addresses from a string and replace them with a placeholder.
    
    Args:
        text (str): The input text containing email addresses
        replacement (str): The placeholder to use. Defaults to "[EMAIL]"
        
    Returns:
        str: The text with all email addresses replaced
    """
    import re
    
    # Comprehensive pattern to match most email formats
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    
    # Replace all matches with the placeholder
    cleaned_text = re.sub(email_pattern, replacement, text)
    
    return cleaned_text

def filter_personal_info(email_body: str, user_email: str) -> str:
    """
    Remove personal information from email body:
    - User's name (extracted from email)
    - User's email address
    - LinkedIn profile URLs
    """
    import re
    logger.info(f"Filtering personal info from email body for {user_email}")

    if not email_body or not user_email:
        return email_body

    if isinstance(email_body, list):
        email_body = email_body[0]
    # Remove user's email address
    email_body = email_body.replace(user_email, "[EMAIL]")
    # Remove LinkedIn profile URLs
    linkedin_pattern = r'https?://(?:www\.)?linkedin\.com/in/[^\s<>"]+'
    email_body = re.sub(linkedin_pattern, "[LINKEDIN]", email_body)
    email_body = clean_utf8(email_body)
    return email_body


def clean_email(email_body: str) -> list:
    import spacy
    from spacy_cleaner import processing, Cleaner

    # First remove HTML tags if present
    email_body = re.sub(r'<[^>]+>', ' ', email_body)
    
    # Common patterns that indicate the start of a quoted message
    quote_patterns = [
        # Reply headers
        r'On .+wrote:',              # "On Monday, John wrote:"
        r'\w+ \w+ \d+:\d+ [AP]M.*wrote',  # Date/time patterns like "Feb 11:35 PM Lianna wrote"
        r'From: .+Sent: .+To: ',     # Outlook style headers
        
        # Forwarded content markers
        r'-{3,}Forwarded Message-{3,}',
        r'-{3,}Original Message-{3,}',
        
        # Quote markers
        r'^\s*>.+$',                 # Lines starting with >
        r'^-----Original Message-----$',

        # Common date formats in replies
        r'\d{1,2}/\d{1,2}/\d{2,4}.+wrote',
        r'At \d{1,2}:\d{2} [AP]M .+wrote',

        # Other delimiters
        r'_{5,}',                    # Underscores as separators
        r'={5,}',                    # Equal signs as separators
    ]
    
    # Find the earliest quote marker
    earliest_pos = len(email_body)
    matched_pattern = None
    
    new_email_body = email_body

    for pattern in quote_patterns:
        matches = list(re.finditer(pattern, email_body, re.MULTILINE | re.IGNORECASE))
        for match in matches:
            if match.start() < earliest_pos:
                earliest_pos = match.start()
                matched_pattern = pattern
    
    # If we found a quotation marker, truncate the email
    if matched_pattern and earliest_pos < len(email_body):
        trimmed_body = email_body[:earliest_pos].strip()
        if trimmed_body:
            new_email_body = trimmed_body
    
    # Plan B: If no patterns matched or if truncating removed all content,
    # look for empty lines as separators between messages
    if not new_email_body or not matched_pattern or not email_body[:earliest_pos].strip():
        # Split by double newlines (paragraph breaks)
        paragraphs = re.split(r'\n\s*\n', email_body)
        # Return just the first paragraph if it exists and isn't too short
        if paragraphs and len(paragraphs[0]) > 10:  # Arbitrary minimum length
            #logger.error("paragraphs[0].strip()", paragraphs[0].strip())
            new_email_body = paragraphs[0].strip()
    
    # If all else fails, return the original (or truncated) content
    if not new_email_body:
        email_body = email_body[:earliest_pos].strip() if matched_pattern else email_body.strip()
    else:
        email_body = new_email_body

    try:
        model = spacy.load("en_core_web_sm")
        pipeline = Cleaner(
            model,
            processing.remove_stopword_token,
            processing.remove_punctuation_token,
            processing.remove_number_token,
        )
        #logger.error("email body: %s", email_body)
        return pipeline.clean([email_body])
    except Exception as e:
        logger.error("Error cleaning email: %s", e)
    return []


def get_word_frequency(cleaned_email):
    try:
        word_dict = {}
        for word in cleaned_email[0].split(" "):
            if word not in word_dict:
                word_dict[word] = 1
            else:
                word_dict[word] += 1

        word_dict_sorted = sorted(
            word_dict.items(), key=lambda item: item[1], reverse=True
        )
        return word_dict_sorted
    except Exception as e:
        logger.error("Error getting word frequency: %s", e)
    return []


def get_top_word_in_email_body(msg_id, msg):
    try:
        parts = get_email_parts(msg)
        if parts:
            for part in parts:
                if part.get("mimeType") not in [
                    "text/plain",
                    "text/html",
                ]:
                    continue
                if part.get("mimeType") and part.get("mimeType") in [
                    "text/plain",
                    "text/html",
                ]:
                    data = base64.urlsafe_b64decode(
                        part.get("body", {}).get("data", {})
                    ).decode("utf-8")
                    # Parse the content with BeautifulSoup
                    soup = BeautifulSoup(data, "html.parser")
                    # Extract the plain text from the HTML content
                    email_text = soup.get_text()
                    cleaned_text = clean_email(email_text)

                    if cleaned_text:
                        word_frequency = get_word_frequency(cleaned_text)
                        top_capitalized_word = get_top_consecutive_capitalized_words(
                            word_frequency
                        )
                        if not top_capitalized_word:
                            if len(cleaned_text) > 0:
                                try:
                                    return cleaned_text[0][0]
                                except IndexError:
                                    return cleaned_text[0]
                        return top_capitalized_word
    except Exception as e:
        logger.error("Error getting top word: %s", e)
    return ""


def get_company_name(id, msg, subject_line):
    try:
        top_word = get_top_word_in_email_body(id, msg)
        from_address = get_email_from_address(msg)
        domain = get_email_domain_from_address(from_address)
        if not top_word or top_word[0].islower():
            # no top word, or top word is not capitalized
            if is_generic_email_domain(domain):
                # if generic ATS domain like workday, greenhouse, etc.,
                # check the last capitalized word(s) in the subject line
                return get_last_capitalized_words_in_line(subject_line) or ""
            return domain.split(".")[0]
        return top_word
    except Exception as e:
        logger.error("Error getting company name: %s", e)
    return ""


def get_top_consecutive_capitalized_words(tuples_list):
    """
    Helper function to parse company name from an email.
    We only want the top capitalized words that appear consecutively and with the same frequency.
    """
    try:
        result = []
        temp_group = []
        max = float("-inf")
        for i, (first, second) in enumerate(tuples_list):
            is_capitalized = first and first[0].isupper()

            if is_capitalized:
                if not temp_group:
                    max = second
                    temp_group.append((first, second))
                if temp_group and temp_group[-1][1] == second:
                    # Add to the current group if criteria match
                    temp_group.append((first, second))
                if second < max:
                    break
                result.append(first)
        return " ".join(result)
    except Exception as e:
        logger.error("Error getting top consecutive capitalized words: %s", e)
    return ""

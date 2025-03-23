import google.generativeai as genai
import time
import json
from google.ai.generativelanguage_v1beta2 import GenerateTextResponse
import logging

from utils.config_utils import get_settings

settings = get_settings()

# Configure Google Gemini API
genai.configure(api_key=settings.GOOGLE_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash-lite")
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

def process_email(email_text):
    prompt = f"""
        Extract the company name, job application status, and job title (role) from the following email. 
        Job application status can be a value from the following list:
        ["rejected", "no response", "request for availability", "interview scheduled", "offer"]
        Note that "no response" means that there is only a neutral, automated or human confirmation of the application being received.
        Note that "interview scheduled" implies a calendar invite with a meeting date and time has been sent.
        Note that "request for availability" implies waiting on the candidate to provide their availability.
        Note that job_title is the role that the user is applying for Ex: "Software Engineer", "Product Engineer", "Data Analyst"
        Provide the output in JSON format, for example:  "company_name": "company_name", "application_status": "status", "job_title": "job_title"
        Remove backticks. Only use double quotes. Enclose key and value pairs in a single pair of curly braces.
        If the email is obviously not related to a job application, return an empty pair of curly braces like this {{}}
        Email: {email_text}
    """

    retries = 3  # Max retries
    delay = 60  # Initial delay
    for attempt in range(retries):
        try:
            logger.info("Calling generate_content")
            response: GenerateTextResponse = model.generate_content(prompt)
            response.resolve()
            response_json: str = response.text
            logger.info("Received response from model: %s", response_json)
            if response_json:
                cleaned_response_json = (
                    response_json.replace("json", "")
                    .replace("`", "")
                    .replace("'", '"')
                    .strip()
                )
                cleaned_response_json = (
                    response_json.replace("json", "")
                    .replace("`", "")
                    .replace("'", '"')
                    .strip()
                )
                logger.info("Cleaned response: %s", cleaned_response_json)
                return json.loads(cleaned_response_json)
            else:
                logger.error("Empty response received from the model.")
                return None
        except Exception as e:
            if "429" in str(e):
                logger.warning(
                    f"Rate limit hit. Retrying in {delay} seconds (attempt {attempt + 1})."
                )
                time.sleep(delay)
            else:
                logger.error(f"process_email exception: {e}")
                return None
    logger.error(f"Failed to process email after {retries} attempts.")
    return None


import google.generativeai as genai
import time
import json
import logging
from google.ai.generativelanguage_v1beta2 import GenerateTextResponse
from playwright.sync_api import Playwright
from browserbase import Browserbase
from typing import List, Dict, Tuple
from pathlib import Path
from playwright.sync_api import sync_playwright
from utils.tech_spec_utils import get_replication_steps, get_summary

from utils.config_utils import get_settings

settings = get_settings()

# Configure Google Gemini API
genai.configure(api_key=settings.GOOGLE_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash-lite")
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Initialize Browserbase client at module level
bb = Browserbase(api_key=settings.BROWSERBASE_API_KEY)

def extract_job_info_from_email(email_content: str) -> Tuple[str, str]:
    """
    Extract company name and job title from application confirmation email.
    Uses Gemini to parse the email content.
    """
    prompt = (
        "Extract the company name and job title from this application confirmation email.\n"
        "Return the result in this exact format: COMPANY_NAME|JOB_TITLE\n\n"
        f"Email content:\n{email_content}"
    )
    
    retries = 3
    delay = 60  # Start with 60 second delay
    
    for attempt in range(retries):
        try:
            logger.info(f"Attempt {attempt + 1} to extract job info")
            response = model.generate_content(prompt)
            response.resolve()
            result = response.text.strip()
            logger.info(f"Response: {result}")
            
            # Clean up the response to ensure it's in the correct format
            result = result.replace("```", "").replace("json", "").strip()
            company_name, job_title = result.split('|')
            return company_name.strip(), job_title.strip()
            
        except Exception as e:
            if "429" in str(e):
                logger.warning(f"Rate limit hit. Retrying in {delay} seconds (attempt {attempt + 1})")
                time.sleep(delay)
                delay *= 2  # Exponential backoff
            else:
                logger.error(f"Error extracting job info: {str(e)}")
                if attempt == retries - 1:  # Last attempt
                    raise
                time.sleep(delay)
    
    # If all retries failed, return unknown values
    logger.error("Failed to extract job info after all retries")
    return "unknown", "unknown"



def scrape_job_description_with_playwright(playwright: Playwright, url: str) -> Tuple[str, str]:
    """
    Scrape job description from a given URL using Browserbase.
    Takes a Playwright instance as a parameter.
    """
    # Create a session using the module-level client
    session = bb.sessions.create(project_id=settings.BROWSERBASE_PROJECT_ID)
    logger.info(f"Session replay URL: https://browserbase.com/sessions/{session.id}")

    try:
        # Connect to the remote session
        chromium = playwright.chromium
        browser = chromium.connect_over_cdp(session.connect_url)
        context = browser.contexts[0]
        page = context.pages[0]

        # Navigate to the job posting
        page.goto(url)
        
        # Extract and summarize job description
        raw_description = extract_job_description(page)
        summary = summarize_job_description(raw_description)
        
        return raw_description, summary
        
    finally:
        # Close the browser
        page.close()
        browser.close()
        logger.info("Browser session closed")


def extract_job_description(page) -> str:
    """
    Extract the job description text from the page.
    """
    # Common selectors for job description sections
    selectors = [
        '[data-test="jobDescriptionText"]',  # LinkedIn
        '.job-description',  # Common class
        '#job-description',  # Common ID
        '[class*="description"]',  # Class containing 'description'
        '[id*="description"]',  # ID containing 'description'
        'article',  # Common for job postings
        '.content',  # Common content class
    ]
    
    # Try each selector
    for selector in selectors:
        try:
            element = page.query_selector(selector)
            if element:
                text = element.inner_text()
                if len(text) > 100:  # Basic validation that we found actual content
                    return text
        except Exception as e:
            logger.warning(f"Failed to extract with selector {selector}: {str(e)}")
            continue
    
    # Fallback: get all text content
    return page.inner_text()

def summarize_job_description(job_description: str) -> str:
    """
    Use Gemini to generate a concise summary of the job description.
    """
    prompt = (
        "Generate a concise summary of this job description, focusing on:\n"
        "1. Key responsibilities\n"
        "2. Required qualifications\n"
        "3. Company culture/benefits\n"
        "4. Location/remote policy\n\n"
        f"Job Description:\n{job_description}\n\n"
        "Return a well-formatted summary with clear sections."
    )
    
    response = model.generate_content(prompt)
    response.resolve()
    return response.text.strip()

def get_false_positive_file_path() -> Path:
    """Get the path to the false positive IDs file."""
    return Path("backend/data/false_positive_ids.json")

def load_false_positive_ids() -> set:
    """Load the set of false positive email IDs."""
    file_path = get_false_positive_file_path()
    if not file_path.exists():
        return set()
    
    try:
        with open(file_path, 'r') as f:
            return set(json.load(f))
    except Exception as e:
        logger.error(f"Error loading false positive IDs: {e}")
        return set()

def save_false_positive_ids(ids: set):
    """Save the set of false positive email IDs."""
    file_path = get_false_positive_file_path()
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(file_path, 'w') as f:
            json.dump(list(ids), f)
    except Exception as e:
        logger.error(f"Error saving false positive IDs: {e}")

def scrape_job_posting(playwright: Playwright, job_title: str) -> Tuple[str, dict]:
    """
    Scrape job posting from Apero Health's YC jobs page.
    Takes a Playwright instance and job title as parameters.
    """
    logger.info(f"Starting job posting scrape for title: {job_title}")
    
    # Create a session using the module-level client
    session = bb.sessions.create(project_id=settings.BROWSERBASE_PROJECT_ID)
    logger.info(f"Created Browserbase session: {session.id}")
    logger.info(f"Session replay URL: https://browserbase.com/sessions/{session.id}")

    try:
        # Connect to the remote session
        logger.info("Connecting to remote browser session")
        chromium = playwright.chromium
        browser = chromium.connect_over_cdp(session.connect_url)
        context = browser.contexts[0]
        page = context.pages[0]
        logger.info("Successfully connected to remote browser session")

        # Navigate to the specific job posting
        url = "https://www.ycombinator.com/companies/apero-health/jobs/o2arkMCAw-senior-software-engineer-backend"
        logger.info(f"Navigating to job posting URL: {url}")
        page.goto(url)
        logger.info("Successfully loaded job posting page")
        
        # Wait for the job description to load
        logger.info("Waiting for job description section to load")
        page.wait_for_selector('h2.ycdc-section-title', timeout=10000)
        logger.info("Job description section loaded")
        
        # Get the job description text
        logger.info("Looking for 'About the role' section")
        description_element = page.evaluate('''() => {
            // Find all h2 elements with the ycdc-section-title class
            const titles = Array.from(document.querySelectorAll('h2.ycdc-section-title'));
            // Find the one containing "About the role"
            const aboutRoleTitle = titles.find(el => el.textContent.includes('About the role'));
            if (!aboutRoleTitle) return null;
            
            // Get the next element
            const nextElement = aboutRoleTitle.nextElementSibling;
            return nextElement ? nextElement.textContent : null;
        }''')
        
        if description_element:
            logger.info("Found job description content")
            description = description_element
            logger.info(f"Extracted job description (length: {len(description)} chars)")
            
            logger.info("Parsing job details with Gemini")
            prompt = f"""
            Parse the following job posting and extract the details in a structured format.
            Return the result in this exact JSON format:
            {{
                "title": "job title",
                "salary": "salary range",
                "location": "job location",
                "job_type": "full-time/part-time/etc",
                "experience": "experience requirement",
                "description": "full job description"
            }}

            Job Posting Content:
            {description}
            """
            try:
                response = model.generate_content(prompt)
                response.resolve()
                response_text = response.text.strip()
                logger.info(f"Received response from Gemini: {response_text[:100]}...")
                
                # Clean up the response text to ensure it's valid JSON
                response_text = response_text.replace("```json", "").replace("```", "").strip()
                job_details = json.loads(response_text)
                logger.info("Successfully parsed job details with Gemini")
            except Exception as e:
                logger.error(f"Error parsing Gemini response: {str(e)}")
                logger.error(f"Raw response: {response_text if 'response_text' in locals() else 'No response'}")
                job_details = {
                    "title": job_title,
                    "salary": "Not specified",
                    "location": "Not specified",
                    "job_type": "Not specified",
                    "experience": "Not specified",
                    "description": description
                }
        else:
            logger.warning("Could not find 'About the role' section or its content")
            description = "No job description found"
            job_details = {
                "title": job_title,
                "salary": "Not specified",
                "location": "Not specified",
                "job_type": "Not specified",
                "experience": "Not specified",
                "description": "No job description found"
            }
        
        logger.info("Job posting scrape completed successfully")
        return description, job_details
        
    except Exception as e:
        logger.error(f"Error during job posting scrape: {str(e)}")
        raise
    finally:
        # Close the browser
        logger.info("Closing browser session")
        page.close()
        browser.close()
        logger.info("Browser session closed")

def process_email(email_text, message_id: str = None):
    """
    Process an email to extract job application status.
    Company name and job title will be extracted separately using job scraping functionality.
    """
    # Check if this is a known false positive
    if message_id:
        false_positive_ids = load_false_positive_ids()
        if message_id in false_positive_ids:
            logger.info(f"Skipping known false positive email: {message_id}")
            return {"application_status": "False positive"}
    
    # Extract application status using Gemini
    prompt = f"""
        Extract the job application status from the following email. 
        Job application status must be one of these exact values:
        [
            "False positive",
            "Application confirmation",
            "Rejection",
            "Availability request",
            "Information request",
            "Assessment sent",
            "Interview invitation",
            "Did not apply - they reached out",
            "Action required from company",
            "Hiring freeze notification",
            "Withdrew application",
            "Offer"
        ]
        
        Rules for determining status:
        - "False positive" if the email is not related to a job application
        - "Application confirmation" for standard "we received your application" emails
        - "Rejection" for any explicit rejection or "not moving forward" message
        - "Availability request" when company asks for candidate's availability
        - "Information request" when company needs additional information
        - "Assessment sent" when company sends a test/assessment
        - "Interview invitation" when company invites to interview
        - "Did not apply - they reached out" when company initiated contact
        - "Action required from company" when waiting on company's response
        - "Hiring freeze notification" when position is frozen/closed
        - "Withdrew application" when candidate withdrew
        - "Offer" when a job offer is extended
        
        Provide the output in JSON format with only the application_status field.
        Example: {{"application_status": "Application confirmation"}}
        
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
                result = json.loads(cleaned_response_json)
                
                # If this is a false positive and we have a message ID, save it
                if message_id and result.get("application_status") == "False positive":
                    false_positive_ids = load_false_positive_ids()
                    false_positive_ids.add(message_id)
                    save_false_positive_ids(false_positive_ids)
                    logger.info(f"Added message ID {message_id} to false positives list")
                
                
                # If we have a valid job application (not a false positive), try to get the job summary
                if result and result.get("application_status") and result["application_status"] != "False positive":
                    logger.info("Valid job application found, attempting to get job summary")
                    try:
                        # Extract company and job title from email
                        logger.info(f"Extracting company name and job title from email text")
                        company_name, job_title = extract_job_info_from_email(email_text)
                        logger.info(f"Extracted - Company: {company_name}, Title: {job_title}")
                        
                        # Initialize Playwright and perform job scraping
                        raw_description = ""
                        # Scrape job posting from Apero's YC page
                        logger.info("Scraping job posting from Apero's YC page")
                        steps = get_replication_steps(url="https://en.m.wikipedia.org/wiki/Kintsugi")
                        raw_description = get_summary(steps) + "\n" + "".join(steps)
                        
                        # Add company name, job title, and summary to result
                        result["company_name"] = company_name  # Use actual company name from email
                        result["job_title"] = job_title
                        result["job_summary"] = raw_description  # Use the raw description as the summary
                            
                    except Exception as e:
                        logger.error(f"Error getting job summary: {str(e)}")
                        result["job_summary"] = ""
                else:
                    logger.info("Not a valid job application or false positive, skipping job summary")
                
                return result
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


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

def search_job_posting_with_playwright(playwright: Playwright, company_name: str, job_title: str) -> List[Dict[str, str]]:
    """
    Search for job posting using Google via Browserbase.
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

        # Construct search query
        search_query = f"{company_name} {job_title} job posting careers"
        search_url = f"https://www.google.com/search?q={search_query.replace(' ', '+')}"
        
        # Navigate to Google search
        page.goto(search_url)
        
        # Wait for search results to load
        page.wait_for_selector('div.g')
        
        # Extract search results
        results = []
        search_elements = page.query_selector_all('div.g')
        
        for element in search_elements[:5]:  # Get top 5 results
            try:
                title_element = element.query_selector('h3')
                link_element = element.query_selector('a')
                snippet_element = element.query_selector('div.VwiC3b')
                
                if title_element and link_element and snippet_element:
                    title = title_element.inner_text()
                    url = link_element.get_attribute('href')
                    snippet = snippet_element.inner_text()
                    
                    # Only include results that look like job postings
                    if any(keyword in title.lower() for keyword in ['job', 'career', 'position', 'opening']):
                        results.append({
                            'title': title,
                            'url': url,
                            'snippet': snippet
                        })
            except Exception as e:
                logger.warning(f"Failed to extract search result: {str(e)}")
                continue
        
        return results
        
    finally:
        # Close the browser
        page.close()
        browser.close()
        logger.info("Browser session closed")

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

def select_relevant_job_url(search_results: List[Dict[str, str]], company_name: str, job_title: str) -> str:
    """
    Use Gemini to analyze search results and select the most relevant job posting URL.
    """
    # Format search results
    formatted_results = "\n".join([
        f"Title: {r['title']}\nURL: {r['url']}\nSnippet: {r['snippet']}\n"
        for r in search_results
    ])
    
    prompt = (
        f"Given the following Google search results for \"{company_name} {job_title}\", \n"
        "select the most relevant job posting URL. Consider:\n"
        "1. Official company career pages or ATS systems (like Greenhouse, Workday, etc.)\n"
        "2. Relevance to the specific company and job title\n"
        "3. Recency of the posting\n\n"
        f"Search Results:\n{formatted_results}\n\n"
        "Return only the URL of the most relevant job posting."
    )
    
    response = model.generate_content(prompt)
    response.resolve()
    return response.text.strip()

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
                        
                        # Initialize Playwright and perform job search and scraping
                        with sync_playwright() as playwright:
                            # Search for job posting
                            logger.info("Searching for job posting")
                            search_results = search_job_posting_with_playwright(playwright, company_name, job_title)
                            
                            if search_results:
                                logger.info(f"Found {len(search_results)} search results")
                                # Select most relevant URL
                                logger.info("Selecting most relevant URL")
                                selected_url = select_relevant_job_url(search_results, company_name, job_title)
                                logger.info(f"Selected URL: {selected_url}")
                                
                                # Scrape job description
                                logger.info("Scraping job description")
                                raw_description, summary = scrape_job_description_with_playwright(playwright, selected_url)
                                
                                # Add company name, job title, and summary to result
                                result["company_name"] = company_name
                                result["job_title"] = job_title
                                result["job_summary"] = summary
                            else:
                                logger.warning("No search results found for job posting")
                                result["job_summary"] = ""
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


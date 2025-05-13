import os
from playwright.sync_api import Playwright
from browserbase import Browserbase
from fastapi import APIRouter, Depends, Request, BackgroundTasks, HTTPException
from slowapi import Limiter
from slowapi.util import get_remote_address
import logging
from session.session_layer import validate_session
import openai
from typing import List, Dict, Tuple
from utils.email_utils import get_email
from utils.auth_utils import AuthenticatedUser
from google.oauth2.credentials import Credentials
import json
from utils.config_utils import get_settings
from google.auth.transport.requests import Request as GoogleRequest
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import base64
import pickle
import os.path
from fastapi import APIRouter, Depends, Request, BackgroundTasks, HTTPException
from slowapi import Limiter
from slowapi.util import get_remote_address
from utils.email_utils import get_email
from utils.auth_utils import AuthenticatedUser
from google.oauth2.credentials import Credentials
import json
limiter = Limiter(key_func=get_remote_address)
TOKEN_PICKLE_FILE = 'token.pickle'
# Logger setup
logger = logging.getLogger(__name__)
# Get settings
settings = get_settings()
# FastAPI router
router = APIRouter()

def get_gmail_service():
    """
    Get or create Gmail API service instance.
    Handles authentication and token refresh.
    """
    creds = None

    # Load existing token if available
    if os.path.exists(TOKEN_PICKLE_FILE):
        with open(TOKEN_PICKLE_FILE, 'rb') as token:
            creds = pickle.load(token)
    
    # Refresh or create new credentials if needed
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(GoogleRequest())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(settings.CLIENT_SECRETS_FILE,
        settings.GOOGLE_SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for future use
        with open(TOKEN_PICKLE_FILE, 'wb') as token:
            pickle.dump(creds, token)
    
    return build('gmail', 'v1', credentials=creds)

def get_email_content(message_id: str) -> str:
    """
    Fetch email content from Gmail using message ID.
    
    Args:
        message_id: Gmail message ID
    
    Returns:
        str: Decoded email content
    """
    try:
        service = get_gmail_service()
        
        # Get the message
        message = service.users().messages().get(
            userId='me',
            id=message_id,
            format='full'
        ).execute()
        
        # Extract the email body
        if 'payload' in message and 'parts' in message['payload']:
            parts = message['payload']['parts']
            for part in parts:
                if part['mimeType'] == 'text/plain':
                    data = part['body'].get('data', '')
                    if data:
                        return base64.urlsafe_b64decode(data).decode('utf-8')
        
        # If no parts found, try to get the body directly
        if 'payload' in message and 'body' in message['payload']:
            data = message['payload']['body'].get('data', '')
            if data:
                return base64.urlsafe_b64decode(data).decode('utf-8')
        
        raise HTTPException(status_code=404, detail="Email content not found")
        
    except Exception as e:
        logger.error(f"Error fetching email content: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching email: {str(e)}")

def extract_job_description(page) -> str:
    """
    Extract the job description text from the page.
    Uses common selectors for job description sections.
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

def summarize_job_description(description: str) -> str:
    """
    Use OpenAI to generate a concise summary of the job description.
    """
    client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
    
    prompt = (
        "Please provide a concise summary of this job description, focusing on:\n"
        "1. Key responsibilities\n"
        "2. Required qualifications\n"
        "3. Preferred qualifications\n"
        "4. Any notable benefits or company information\n\n"
        f"Job Description:\n{description}\n\n"
        "Format the summary in clear sections with bullet points."
    )
    
    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": "You are a job description analyzer that creates clear, concise summaries."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )
    
    return response.choices[0].message.content.strip()

def select_relevant_job_url(search_results: List[Dict[str, str]], company_name: str, job_title: str) -> str:
    """
    Use OpenAI to analyze search results and select the most relevant job posting URL.

    Args:
        search_results: List of dictionaries containing 'title', 'url', and 'snippet' for each result
        company_name: Name of the company from the confirmation email
        job_title: Job title from the confirmation email
    
    Returns:
        str: The most relevant job posting URL
    """
    client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
    
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
    
    response = client.chat.completions.create(
        model="gpt-4-turbo-preview",  # Using GPT-4 for better accuracy
        messages=[
            {"role": "system", "content": "You are a job search assistant that helps identify the most relevant job posting URLs."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.1  # Low temperature for more consistent results
    )
    
    return response.choices[0].message.content.strip()

def extract_job_info_from_email(email_content: str) -> Tuple[str, str]:
    """
    Extract company name and job title from application confirmation email.
    Uses OpenAI to parse the email content.
    """
    client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
    
    prompt = (
        "Extract the company name and job title from this application confirmation email.\n"
        "Return the result in this exact format: COMPANY_NAME|JOB_TITLE\n\n"
        f"Email content:\n{email_content}"
    )
    
    response = client.chat.completions.create(
        model="gpt-4-turbo-preview",
        messages=[
            {"role": "system", "content": "You are an email parser that extracts job application information."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.1
    )
    
    result = response.choices[0].message.content.strip()
    company_name, job_title = result.split('|')
    return company_name.strip(), job_title.strip()

def run(playwright: Playwright, email_content: str) -> Tuple[str, str]:
    """
    Run the complete job scraping workflow:
    1. Extract company and job title from email
    2. Search for job posting
    3. Select most relevant URL
    4. Scrape and summarize job description
    
    Args:
        playwright: Playwright instance
        email_content: Content of the application confirmation email
    
    Returns:
        Tuple of (raw_description, summary)
    """
    try:
        # Step 1: Extract job info from email
        company_name, job_title = extract_job_info_from_email(email_content)
        logger.info(f"Extracted job info - Company: {company_name}, Title: {job_title}")
        
        # Step 2: Search for job posting
        search_results = search_job_posting(company_name, job_title)
        if not search_results:
            raise Exception("No relevant job postings found")
        
        # Step 3: Select most relevant URL
        selected_url = select_relevant_job_url(search_results, company_name, job_title)
        logger.info(f"Selected URL: {selected_url}")
        
        # Step 4: Scrape and summarize job description
        # Create a session on Browserbase
        bb = Browserbase(api_key=settings.BROWSERBASE_API_KEY)
        session = bb.sessions.create(project_id=settings.BROWSERBASE_PROJECT_ID)
        logger.info(f"Session replay URL: https://browserbase.com/sessions/{session.id}")

        try:
            # Connect to the remote session
            chromium = playwright.chromium
            browser = chromium.connect_over_cdp(session.connect_url)
            context = browser.contexts[0]
            page = context.pages[0]

            # Navigate to the job posting
            page.goto(selected_url)
            
            # Extract the job description
            raw_description = extract_job_description(page)
            
            # Generate summary
            summary = summarize_job_description(raw_description)
            
            return raw_description, summary
            
        finally:
            # Close the browser
            page.close()
            browser.close()
            logger.info("Browser session closed")
            
    except Exception as e:
        logger.error(f"Error in job scraping workflow: {str(e)}")
        raise

@router.post("/process-email")
@limiter.limit("5/minute")
async def process_application_email(
    request: Request,
    background_tasks: BackgroundTasks,
    user_id: str = Depends(validate_session)
):
    """
    Process an application confirmation email and start the job scraping workflow.
    """
    data = await request.json()
    email_content = data.get("email_content")
    
    if not email_content:
        return {"error": "email_content is required"}
    
    # Start the scraping task in the background
    background_tasks.add_task(run, email_content=email_content)
    
    return {
        "status": "success",
        "message": "Job scraping task started"
    }

@router.get("/email/{message_id}")
@limiter.limit("5/minute")
async def get_email_and_scrape(
    request: Request,
    message_id: str,
    background_tasks: BackgroundTasks,
    user_id: str = Depends(validate_session)
):
    """
    Get email content by Gmail message ID and start job scraping process.
    """
    try:
        # Get stored credentials from session
        creds_json = request.session.get("creds")
        if not creds_json:
            raise HTTPException(status_code=401, detail="User not authenticated. Please log in again.")

        # Convert JSON string back to Credentials object
        creds_dict = json.loads(creds_json)
        creds = Credentials.from_authorized_user_info(creds_dict)
        user = AuthenticatedUser(creds)

        # Build Gmail service
        service = build("gmail", "v1", credentials=user.creds)

        # Get email content using existing utility
        msg = get_email(message_id=message_id, gmail_instance=service)
        
        if not msg or not msg.get("text_content"):
            raise HTTPException(status_code=404, detail="Email content not found")

        # Start the scraping task in the background
        background_tasks.add_task(run, email_content=msg["text_content"])
        
        return {
            "status": "success",
            "message": "Email content retrieved and job scraping task started",
            "email_content": msg["text_content"]
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error processing email: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing email: {str(e)}")

async def search_job_posting(company_name: str, job_title: str) -> List[Dict[str, str]]:
    """
    Search for job posting using Google via Browserbase.
    
    Args:
        company_name: Name of the company
        job_title: Title of the job position
    
    Returns:
        List of dictionaries containing search results with 'title', 'url', and 'snippet'
    """
    with playwright() as playwright:
        # Create a session on Browserbase
        bb = Browserbase(api_key=settings.BROWSERBASE_API_KEY)
        session = bb.sessions.create(project_id=settings.BROWSERBASE_PROJECT_ID)
        logger.info(f"Session replay URL: https://browserbase.com/sessions/{session.id}")

        try:
            # Connect to the remote session
            chromium = playwright.chromium
            browser = await chromium.connect_over_cdp(session.connect_url)
            context = browser.contexts[0]
            page = context.pages[0]

            # Construct search query
            search_query = f"{company_name} {job_title} job posting careers"
            search_url = f"https://www.google.com/search?q={search_query.replace(' ', '+')}"
            
            # Navigate to Google search
            await page.goto(search_url)
            
            # Wait for search results to load
            await page.wait_for_selector('div.g')
            
            # Extract search results
            results = []
            search_elements = await page.query_selector_all('div.g')
            
            for element in search_elements[:5]:  # Get top 5 results
                try:
                    title_element = await element.query_selector('h3')
                    link_element = await element.query_selector('a')
                    snippet_element = await element.query_selector('div.VwiC3b')
                    
                    if title_element and link_element and snippet_element:
                        title = await title_element.inner_text()
                        url = await link_element.get_attribute('href')
                        snippet = await snippet_element.inner_text()
                        
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
            await browser.close()
            logger.info("Browser session closed")

def search_email_by_subject(subject: str) -> str:
    """
    Search for an email by subject line and return its message ID.
    """
    service = get_gmail_service()
    
    # Search for emails with the subject
    query = f'subject:"{subject}"'
    results = service.users().messages().list(userId='me', q=query).execute()
    
    messages = results.get('messages', [])
    if not messages:
        raise Exception(f"No emails found with subject: {subject}")
    
    # Get the most recent email
    message = messages[0]
    message_id = message['id']
    
    # Get full message details to verify subject
    msg = service.users().messages().get(userId='me', id=message_id).execute()
    headers = msg['payload']['headers']
    subject_header = next((h['value'] for h in headers if h['name'].lower() == 'subject'), None)
    
    if not subject_header:
        raise Exception("Could not find subject in email headers")
    
    print(f"\nFound email with subject: {subject_header}")
    return message_id

if __name__ == "__main__":
    import asyncio
    from fastapi import Request
    from google.oauth2.credentials import Credentials
    import json
    
    async def scrape_single_email(message_id: str):
        # Create a mock request with session data
        request = Request({"type": "http", "method": "GET"})
        request.session = {
            "creds": json.dumps({
                "token": "your_token_here",
                "refresh_token": "your_refresh_token_here",
                "token_uri": "https://oauth2.googleapis.com/token",
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_API_KEY,
                "scopes": settings.GOOGLE_SCOPES
            })
        }
        
        try:
            # Call the endpoint
            response = await get_email_and_scrape(
                request=request,
                message_id=message_id,
                background_tasks=BackgroundTasks(),
                user_id="test_user"
            )
            
            print("\nEmail Content:")
            print(response["email_content"])
            
        except Exception as e:
            print(f"Error: {str(e)}")
    
    try:
        # Search for the email by subject
        subject = "Thank you for application to Snorkel AI"
        message_id = search_email_by_subject(subject)
        print(f"\nMessage ID: {message_id}")
        
        # Run the async function to scrape the email
        asyncio.run(scrape_single_email(message_id))
        
    except Exception as e:
        print(f"Error: {str(e)}")

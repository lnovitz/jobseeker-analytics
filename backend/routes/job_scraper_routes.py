import os
from playwright.sync_api import Playwright, sync_playwright
from browserbase import Browserbase
from fastapi import APIRouter, Depends, Request, BackgroundTasks
from slowapi import Limiter
from slowapi.util import get_remote_address
import logging
from utils.config_utils import get_settings
from session.session_layer import validate_session
import openai
from typing import List, Dict, Tuple

limiter = Limiter(key_func=get_remote_address)

# Logger setup
logger = logging.getLogger(__name__)

# Get settings
settings = get_settings()
APP_URL = settings.APP_URL
BROWSERBASE_API_KEY = settings.BROWSERBASE_API_KEY
BROWSERBASE_PROJECT_ID = settings.BROWSERBASE_PROJECT_ID
OPENAI_API_KEY = settings.OPENAI_API_KEY

# FastAPI router
router = APIRouter()

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
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    
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
        model="gpt-4-turbo-preview",
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
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    
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

def run(playwright: Playwright, url: str = "https://browserbase.com/") -> Tuple[str, str]:
    """
    Run the job scraping process and return both raw description and summary.
    """
    # Create a session on Browserbase
    bb = Browserbase(api_key=BROWSERBASE_API_KEY)
    session = bb.sessions.create(project_id=BROWSERBASE_PROJECT_ID)
    print("Session replay URL:", f"https://browserbase.com/sessions/{session.id}")

    try:
        # Connect to the remote session
        chromium = playwright.chromium
        browser = chromium.connect_over_cdp(session.connect_url)
        context = browser.contexts[0]
        page = context.pages[0]

        # Execute Playwright actions on the remote browser tab
        page.goto(url)
        
        # Extract the job description
        raw_description = extract_job_description(page)
        
        # Generate summary
        summary = summarize_job_description(raw_description)
        
        return raw_description, summary
        
    finally:
        # Close the browser
        page.close()
        browser.close()
        print("Done!")

@router.post("/tasks")
@limiter.limit("5/minute")
async def create_scraping_task(
    request: Request,
    background_tasks: BackgroundTasks,
    user_id: str = Depends(validate_session)
):
    """
    Create a new job scraping task.
    """
    data = await request.json()
    url = data.get("url")
    if not url:
        return {"error": "URL is required"}
    
    # Add the scraping task to background tasks
    background_tasks.add_task(run, url=url)
    return {"status": "Task created successfully"}

@router.get("/tasks/{task_id}")
@limiter.limit("5/minute")
async def get_task_status(
    request: Request,
    task_id: str,
    user_id: str = Depends(validate_session)
):
    """
    Get the status and results of a scraping task.
    """
    # TODO: Implement task status tracking
    return {"status": "pending", "message": "Task status tracking not implemented yet"}

if __name__ == "__main__":
    with sync_playwright() as playwright:
        raw_desc, summary = run(playwright)
        print("\nRaw Description:")
        print(raw_desc)
        print("\nSummary:")
        print(summary)

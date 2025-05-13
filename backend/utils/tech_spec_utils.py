import logging
from typing import Dict, List, Optional
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import re
from browserbase import Browserbase
from utils.config_utils import get_settings
import openai

# Logger setup
logger = logging.getLogger(__name__)
settings = get_settings()

bb = Browserbase(api_key=settings.BROWSERBASE_API_KEY)

def get_summary(steps: List[str]) -> str:
    """
    Generate a concise summary of the webpage's design and technical specifications using OpenAI.
    
    Args:
        steps: List of steps generated from get_replication_steps
        
    Returns:
        str: A 4-sentence summary of the webpage's design and technical specifications
    """
    logger.info("Generating webpage summary using OpenAI")
    
    try:
        # Create a prompt that includes the steps and asks for a specific format
        prompt = f"""Based on these technical specifications and replication steps, provide a 4-sentence summary of the webpage's design and purpose:

{chr(10).join(steps)}

The summary should:
1. Describe the overall purpose and type of webpage
2. Mention key design elements and layout
3. Note any special features or interactive elements
4. Comment on the technical implementation approach

Format the response as 4 clear, concise sentences."""

        # Call OpenAI API
        client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-4.1-nano",
            messages=[
                {"role": "system", "content": "You are a web development expert that creates clear, concise summaries of webpage designs and technical specifications."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=200
        )
        
        summary = response.choices[0].message.content.strip()
        logger.info("Successfully generated webpage summary")
        return summary
        
    except Exception as e:
        logger.error(f"Error generating webpage summary: {str(e)}", exc_info=True)
        raise
    

def get_html(url: str) -> Dict[str, str]:
    """
    Analyze the HTML structure of a webpage and return its technical specifications.
    
    Args:
        url: The URL of the webpage to analyze
        
    Returns:
        Dict containing HTML specifications including DOCTYPE, container structure,
        header elements, content elements, and links
    """
    logger.info(f"Analyzing HTML structure for URL: {url}")
    
    try:
        with sync_playwright() as playwright:
            # Create a session on Browserbase
            session = bb.sessions.create(project_id=settings.BROWSERBASE_PROJECT_ID)
            logger.info(f"Session replay URL: https://browserbase.com/sessions/{session.id}")

            try:
                # Connect to the remote session
                chromium = playwright.chromium
                browser = chromium.connect_over_cdp(session.connect_url)
                context = browser.contexts[0]
                page = context.pages[0]

                # Navigate to the URL
                page.goto(url)
                
                # Get the HTML content
                html_content = page.content()
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # Analyze HTML structure
                doctype = soup.find('!DOCTYPE')
                container = soup.find('div', class_=lambda x: x and 'container' in x.lower())
                header = soup.find('h1')
                content = soup.find('p')
                links = soup.find_all('a')
                
                specs = {
                    "doctype": str(doctype) if doctype else "HTML5",
                    "container": {
                        "type": container.name if container else "div",
                        "classes": container.get('class', []) if container else [],
                        "max_width": container.get('style', '').split('max-width:')[1].split(';')[0].strip() if container and 'max-width' in container.get('style', '') else None
                    },
                    "header": {
                        "text": header.text.strip() if header else None,
                        "tag": header.name if header else None
                    },
                    "content": {
                        "text": content.text.strip() if content else None,
                        "tag": content.name if content else None
                    },
                    "links": [{
                        "text": link.text.strip(),
                        "href": link.get('href'),
                        "target": link.get('target')
                    } for link in links]
                }
                assert specs is not None, "get_html returned None"
                return specs
                
            finally:
                # Close the browser
                page.close()
                browser.close()
                logger.info("Browser session closed")
            
    except Exception as e:
        logger.error(f"Error analyzing HTML structure: {str(e)}", exc_info=True)
        raise

def get_css(url: str) -> Dict[str, Dict[str, str]]:
    """
    Analyze the CSS styling of a webpage and return its technical specifications.
    
    Args:
        url: The URL of the webpage to analyze
        
    Returns:
        Dict containing CSS specifications including fonts, colors, and layout properties
    """
    logger.info(f"Analyzing CSS styling for URL: {url}")
    
    try:
        with sync_playwright() as playwright:
            # Create a session on Browserbase
            session = bb.sessions.create(project_id=settings.BROWSERBASE_PROJECT_ID)
            logger.info(f"Session replay URL: https://browserbase.com/sessions/{session.id}")

            try:
                # Connect to the remote session
                chromium = playwright.chromium
                browser = chromium.connect_over_cdp(session.connect_url)
                context = browser.contexts[0]
                page = context.pages[0]

                # Navigate to the URL
                page.goto(url)
                
                # Get computed styles for body
                body_styles = page.evaluate("""() => {
                    const body = document.body;
                    const styles = window.getComputedStyle(body);
                    return {
                        fontFamily: styles.fontFamily,
                        backgroundColor: styles.backgroundColor,
                        color: styles.color,
                        padding: styles.padding,
                        margin: styles.margin,
                        textAlign: styles.textAlign
                    };
                }""")
                
                # Get computed styles for links
                link_styles = page.evaluate("""() => {
                    const link = document.querySelector('a');
                    const styles = window.getComputedStyle(link);
                    return {
                        color: styles.color,
                        textDecoration: styles.textDecoration
                    };
                }""")
                
                specs = {
                    "fonts": {
                        "family": body_styles.get('fontFamily', 'sans-serif'),
                        "size": body_styles.get('fontSize', '16px')
                    },
                    "colors": {
                        "background": body_styles.get('backgroundColor', '#ffffff'),
                        "text": body_styles.get('color', '#222222'),
                        "links": link_styles.get('color', '#0000ee')
                    },
                    "layout": {
                        "padding": body_styles.get('padding', '30px'),
                        "margin": body_styles.get('margin', 'auto'),
                        "text_align": body_styles.get('textAlign', 'center')
                    }
                }
                assert specs is not None, "get_css returned None"
                return specs
                
            finally:
                # Close the browser
                page.close()
                browser.close()
                logger.info("Browser session closed")
            
    except Exception as e:
        logger.error(f"Error analyzing CSS styling: {str(e)}", exc_info=True)
        raise

def get_js(url: str) -> Dict[str, List[str]]:
    """
    Analyze the JavaScript usage on a webpage and return its technical specifications.
    
    Args:
        url: The URL of the webpage to analyze
        
    Returns:
        Dict containing JavaScript specifications including scripts and interactive elements
    """
    logger.info(f"Analyzing JavaScript usage for URL: {url}")
    
    try:
        with sync_playwright() as playwright:
            # Create a session on Browserbase
            session = bb.sessions.create(project_id=settings.BROWSERBASE_PROJECT_ID)
            logger.info(f"Session replay URL: https://browserbase.com/sessions/{session.id}")

            try:
                # Connect to the remote session
                chromium = playwright.chromium
                browser = chromium.connect_over_cdp(session.connect_url)
                context = browser.contexts[0]
                page = context.pages[0]

                # Navigate to the URL
                page.goto(url)
                
                # Get all script tags
                scripts = page.evaluate("""() => {
                    return Array.from(document.getElementsByTagName('script')).map(script => ({
                        src: script.src,
                        type: script.type,
                        content: script.textContent
                    }));
                }""")
                
                # Check for interactive elements
                interactive_elements = page.evaluate("""() => {
                    return {
                        buttons: document.querySelectorAll('button').length,
                        forms: document.querySelectorAll('form').length,
                        inputs: document.querySelectorAll('input').length,
                        eventListeners: document.querySelectorAll('[onclick], [onmouseover], [onmouseout]').length
                    };
                }""")
                
                specs = {
                    "scripts": scripts,
                    "interactive_elements": interactive_elements,
                    "has_javascript": len(scripts) > 0 or any(interactive_elements.values())
                }
                assert specs is not None, "get_js returned None"
                return specs
                
            finally:
                # Close the browser
                page.close()
                browser.close()
                logger.info("Browser session closed")
            
    except Exception as e:
        logger.error(f"Error analyzing JavaScript usage: {str(e)}", exc_info=True)
        raise

def get_responsivity(url: str) -> Dict[str, Dict[str, str]]:
    """
    Analyze the responsive design features of a webpage and return its technical specifications.
    
    Args:
        url: The URL of the webpage to analyze
        
    Returns:
        Dict containing responsive design specifications including viewport settings,
        media queries, and responsive breakpoints
    """
    logger.info(f"Analyzing responsive design for URL: {url}")
    
    try:
        with sync_playwright() as playwright:
            # Create a session on Browserbase
            session = bb.sessions.create(project_id=settings.BROWSERBASE_PROJECT_ID)
            logger.info(f"Session replay URL: https://browserbase.com/sessions/{session.id}")

            try:
                # Connect to the remote session
                chromium = playwright.chromium
                browser = chromium.connect_over_cdp(session.connect_url)
                context = browser.contexts[0]
                page = context.pages[0]

                # Navigate to the URL
                page.goto(url)
                
                # Get viewport meta tag
                viewport = page.evaluate("""() => {
                    const viewport = document.querySelector('meta[name="viewport"]');
                    return viewport ? viewport.content : null;
                }""")
                
                # Get media queries
                media_queries = page.evaluate("""() => {
                    const styleSheets = Array.from(document.styleSheets);
                    const mediaQueries = [];
                    
                    styleSheets.forEach(sheet => {
                        try {
                            const rules = Array.from(sheet.cssRules);
                            rules.forEach(rule => {
                                if (rule instanceof CSSMediaRule) {
                                    mediaQueries.push({
                                        condition: rule.conditionText,
                                        rules: Array.from(rule.cssRules).map(r => r.cssText)
                                    });
                                }
                            });
                        } catch (e) {
                            // Skip cross-origin stylesheets
                        }
                    });
                    
                    return mediaQueries;
                }""")
                
                specs = {
                    "viewport": {
                        "meta": viewport,
                        "has_responsive_viewport": viewport and 'width=device-width' in viewport
                    },
                    "media_queries": media_queries,
                    "is_responsive": len(media_queries) > 0 or (viewport and 'width=device-width' in viewport)
                }
                assert specs is not None, "get_responsivity returned None"
                return specs
                
            finally:
                # Close the browser
                page.close()
                browser.close()
                logger.info("Browser session closed")
            
    except Exception as e:
        logger.error(f"Error analyzing responsive design: {str(e)}", exc_info=True)
        raise

def get_content(url: str) -> Dict[str, str]:
    """
    Extract and analyze the content of a webpage and return its technical specifications.
    
    Args:
        url: The URL of the webpage to analyze
        
    Returns:
        Dict containing content specifications including title, paragraphs, and links
    """
    logger.info(f"Analyzing content for URL: {url}")
    
    try:
        with sync_playwright() as playwright:
            # Create a session on Browserbase
            session = bb.sessions.create(project_id=settings.BROWSERBASE_PROJECT_ID)
            logger.info(f"Session replay URL: https://browserbase.com/sessions/{session.id}")

            try:
                # Connect to the remote session
                chromium = playwright.chromium
                browser = chromium.connect_over_cdp(session.connect_url)
                context = browser.contexts[0]
                page = context.pages[0]

                # Navigate to the URL
                page.goto(url)
                
                # Get page content
                content = page.evaluate("""() => {
                    return {
                        title: document.title,
                        h1: document.querySelector('h1')?.textContent,
                        paragraphs: Array.from(document.querySelectorAll('p')).map(p => p.textContent),
                        links: Array.from(document.querySelectorAll('a')).map(a => ({
                            text: a.textContent,
                            href: a.href
                        }))
                    };
                }""")
                
                specs = {
                    "title": content.get('title', ''),
                    "header": content.get('h1', ''),
                    "paragraphs": content.get('paragraphs', []),
                    "links": content.get('links', [])
                }
                assert specs is not None, "get_content returned None"
                return specs
                
            finally:
                # Close the browser
                page.close()
                browser.close()
                logger.info("Browser session closed")
            
    except Exception as e:
        logger.error(f"Error analyzing content: {str(e)}", exc_info=True)
        raise

def get_replication_steps(url: str) -> List[str]:
    """
    Generate a list of steps to replicate the webpage based on its technical specifications.
    
    Args:
        url: The URL of the webpage to analyze
        
    Returns:
        List of steps to replicate the webpage
    """
    logger.info(f"Generating replication steps for URL: {url}")
    
    try:
        # Get all specifications
        html_specs = get_html(url)
        css_specs = get_css(url)
        js_specs = get_js(url)
        responsive_specs = get_responsivity(url)
        content_specs = get_content(url)
        
        steps = [
            "1. Create basic HTML5 document",
            "2. Add viewport meta tag for responsive design:",
            f"   - Add <meta name='viewport' content='{responsive_specs['viewport']['meta']}'>" if responsive_specs['viewport']['meta'] else "   - Add <meta name='viewport' content='width=device-width, initial-scale=1.0'>",
            "3. Add CSS styling:",
            f"   - Set font family to {css_specs['fonts']['family']}",
            f"   - Set background color to {css_specs['colors']['background']}",
            f"   - Set text color to {css_specs['colors']['text']}",
            f"   - Set link color to {css_specs['colors']['links']}",
            f"   - Add padding: {css_specs['layout']['padding']}",
            f"   - Set text alignment to {css_specs['layout']['text_align']}"
        ]
        
        # Add responsive design steps if needed
        if responsive_specs['media_queries']:
            steps.append("4. Add responsive design rules:")
            for i, query in enumerate(responsive_specs['media_queries'], 1):
                steps.append(f"   {i}. Add media query: {query['condition']}")
                for rule in query['rules']:
                    steps.append(f"      - {rule}")
        
        # Add HTML structure
        steps.append("5. Add HTML structure:")
        steps.append(f"   - Add container div with max-width: {html_specs['container']['max_width']}")
        steps.append(f"   - Add header: {html_specs['header']['text']}")
        
        # Add content from content_specs
        if content_specs['paragraphs']:
            steps.append("   - Add paragraphs:")
            for i, para in enumerate(content_specs['paragraphs'], 1):
                steps.append(f"     {i}. {para}")
        
        # Add links
        steps.append("6. Add links:")
        for link in html_specs['links']:
            steps.append(f"   - Add link to {link['href']} with text: {link['text']}")
        
        # Add JavaScript steps if needed
        if js_specs['has_javascript']:
            steps.append("7. Add JavaScript functionality:")
            for script in js_specs['scripts']:
                if script['src']:
                    steps.append(f"   - Include script: {script['src']}")
                elif script['content']:
                    steps.append(f"   - Add inline script: {script['content'][:100]}...")
            
            if js_specs['interactive_elements']:
                steps.append("   - Add interactive elements:")
                if js_specs['interactive_elements']['buttons']:
                    steps.append(f"     - Add {js_specs['interactive_elements']['buttons']} button(s)")
                if js_specs['interactive_elements']['forms']:
                    steps.append(f"     - Add {js_specs['interactive_elements']['forms']} form(s)")
                if js_specs['interactive_elements']['inputs']:
                    steps.append(f"     - Add {js_specs['interactive_elements']['inputs']} input field(s)")
        
        # Add testing steps
        steps.append("8. Testing and verification:")
        steps.append("   - Test in multiple browsers")
        steps.append("   - Verify responsive design at different viewport sizes")
        steps.append("   - Check all links are working")
        if js_specs['has_javascript']:
            steps.append("   - Verify JavaScript functionality")
        steps.append("   - Compare visual appearance with original")
        
        logger.info("Successfully generated replication steps")
        return steps
        
    except Exception as e:
        logger.error(f"Error generating replication steps: {str(e)}", exc_info=True)
        raise
import time
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from urllib.parse import urlparse

from utils.spinner import Spinner

TITLE_NOT_FOUND_TEXT = "Title not found."

def _build_driver(headless: bool = True) -> webdriver.Firefox:
    """
    Builds and returns a Firefox WebDriver.
    headless=True runs silently with no visible browser window.
    headless=False opens a real Firefox window - useful for debugging.
    """
    
    options = Options()

    if headless:
        options.add_argument("--headless")

    options.add_argument("--width=1920")
    options.add_argument("--height=1080")

    #GeckoDriverManager downloads the right driver for Firefox version
    service = Service(GeckoDriverManager().install())
    driver = webdriver.Firefox(service=service, options=options)

    return driver

def scrape_job_page_dynamic(url: str, headless: bool = True) -> dict:
    """
    Uses Firefox + Selenium to scrape a JS-rendered job page.
    Called automatically by static_scraper.py when BeautifulSoup returns 
    an empty description.

    Returns same dic format as static_scraper:
    { title, description, url }
    """

    print(f"[SELENIUM] Launching Firefox for: {url}")
    driver = None

    try:
        # Lunch browser
        with Spinner("Launching Firefox...", style="hourglass", speed=0.5):
            driver = _build_driver(headless=headless)

        #Wait up to 10 seconds fro the page body to load
        with Spinner(f"Loading page...", style="dots", speed=0.1):
            driver.get(url)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

        #Extra pause for JS content to finish rendering
        with Spinner("Waiting for page content to render...", style="bar", speed=0.08):
            time.sleep(3)

        #Hand the fully rendered HTML to BeautifulSoup
        with Spinner("Extacting job details...", style="dots", speed=0.1):
            soup = BeautifulSoup(driver.page_source, "html.parser")

            # Extract title
            title = TITLE_NOT_FOUND_TEXT
            title_tag = soup.find("h1")
            if title_tag:
                title = title_tag.get_text(strip=True)
            
            #Fallback - check for h4 near redactor-styles (some job boards)
            if not title or title == TITLE_NOT_FOUND_TEXT:
                desc_div = soup.find(attrs={"class": "redactor-styles"})
                if desc_div:
                    h4 = desc_div.find_previous("h4")
                    if h4:
                        title = h4.get_text(strip=True).replace("About the job", "").strip()
            
            #Extract description
            description = ""

            candidate_selectors = [
                {"class": "redactor-styles"},
                {"class": "job-description"},
                {"class": "description"},
                {"class": "job-details"},
                {"id": "job-description"},
                {"class": "posting-description"},
                {"class": "job-content"},
                {"class": "vacancy-description"},
            ]

            for selector in candidate_selectors:
                tag = soup.find(attrs=selector)
                if tag:
                    description = tag.get_text(separator="\n", strip=True)
                    break
            
            #Fallback - grab paragraphs with meaningful content
            if not description:
                paragraphs = soup.find_all("p")
                description = "\n".join(
                    p.get_text(strip=True)
                    for p in paragraphs
                    if len(p.get_text(strip=True))
                )
        
        print(f"[SELENIUM] Done. Title: '{title}")
        print(f"[SELENIUM] Description: '{len(description)} characters extracted")

        return {
            "title": title,
            "description": description,
            "url": url
        }
    
    except Exception as e:
        print(f"[ERROR] Selenium failed: {e}")
        print("[HINT]  Make sure Firefox is installed on your machine.")
        print("[HINT]  GeckoDriver will be downloaded automatically on first run.")
        return {}
    
    finally:
        # Always close the browser - even if something crashed
        if driver:
            with Spinner("Closing Firefox...", style="simple", speed=0.1, done_message="[SELENIUM] Firefox closed."):
                driver.quit()

def scrape_listing_page_dynamic(
    base_url: str,
    keywords: list,
    max_jobs: int = 5
) -> list:
    """
    Uses Firefox + Selenium to scrape a JS-rendered job Listing page.
    Called from main.py when the static listing scraper return 0 results.
    Returns same format as listing_scraper.get_job_listings():
    [{ title, url, keyword_matched }]
    """

    from scraper.listing_scraper import title_matches_keyword, is_blocked_title

    print(f"[SELENIUM] Loading listing page with Firefox: {base_url}")
    driver = None
    all_jobs = []

    try:
        # Lunch browser
        with Spinner("Launching Firefox...", style="hourglass", speed=0.5):
            driver = _build_driver(headless=True)
        
        # Load listing page
        with Spinner("Loading job listing page...", style="dots", speed=0.1):
            driver.get(base_url)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

        # Wait for job cards to finish loading
        with Spinner("Waiting for job listings to load...", style="bar", speed=0.08):
            time.sleep(4)

        # Scrape and filter
        with Spinner("Scanning for matching jobs...", style="dots", speed=0.1):
            soup = BeautifulSoup(driver.page_source, "html.parser")

            # Build domain root for relative URLs
            parsed = urlparse(base_url)
            domain_root = f"{parsed.scheme}://{parsed.netloc}"

            # Scan all links on the page
            all_links = soup.find_all("a", href=True)

            for link in all_links:
                title = link.get_text(strip=True)

                if not title or len(title) < 5:
                    continue

                href = link.get("href", "")
                if not href:
                    continue

                # Build full URL from relative path if needed
                if href.startswith("http"):
                    full_url = href
                elif href.startswith("/"):
                    full_url = domain_root + href
                else:
                    continue

                # Skip duplicates
                if any(j["url"] == full_url for j in all_jobs):
                    continue

                # Skip bloced role types
                if is_blocked_title(title):
                    continue

                # Check against all keywords
                for keyword in keywords:
                    if title_matches_keyword(title, keyword):
                        all_jobs.append({
                            "title": title,
                            "url": full_url,
                            "keyword_matched": keyword
                        })
                        print(f" ✓ Matched: '{title}'")
                        break
                
                if len(all_jobs) >= max_jobs:
                    break
        
        print(f"[SELENIUM] Found {len(all_jobs)} matching job(s).")
        return all_jobs
    
    except Exception as e:
        print(f"[ERROR] Selenium listing scrape failed: {e}")
        print("[HINT]  Make sure Firefox is installed.")
        return []
    
    finally:
        if driver:
            with Spinner("Closing Firefox...", style="simple", speed=0.1, done_message="[SELENIUM] Firefox closed."):
                driver.quit()

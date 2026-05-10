import requests
from bs4 import BeautifulSoup

def scrape_job_page(url: str) -> dict:
    """
    Fetches a job listing page and extracts the job title and description.
    Returns a dict with 'title' and 'description' keys.
    """

    headers = {
        # We pretend to be a browser so the server doesn't immediately block us
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raises an error if status is 4xx/5xx
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Failed to fetch page: {e}")
        return {}

    soup = BeautifulSoup(response.text, "html.parser")

    # --- Extract job title ---
    # Most sites put the job title in an <h1> tag. We try that first.
    title_tag = soup.find("h1")
    title = title_tag.get_text(strip=True) if title_tag else "Title not found"

    # --- Extract job description ---
    # This is the tricky part — every site uses different class names.
    # We try a few common patterns:
    description = ""

    # Common class names used by career pages
    candidate_selectors = [
        {"class": "job-description"},
        {"class": "description"},
        {"class": "job-details"},
        {"id": "job-description"},
        {"class": "posting-description"},
        {"class": "redactor-styles"},
    ]

    for selector in candidate_selectors:
        tag = soup.find(attrs=selector)
        if tag:
            description = tag.get_text(separator="\n", strip=True)
            break

    # Fallback: grab all paragraph text if nothing matched
    if not description:
        paragraphs = soup.find_all("p")
        description = "\n".join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))

    return {
        "title": title,
        "description": description,
        "url": url
    }


# Quick test — run this file directly to try it
if __name__ == "__main__":
    test_url = input("Paste a job listing URL to test: ").strip()
    result = scrape_job_page(test_url)

    print("\n--- RESULTS ---")
    print(f"Title: {result.get('title')}")
    print(f"\nDescription (first 500 chars):\n{result.get('description', '')[:500]}")
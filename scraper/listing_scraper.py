import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

# ─────────────────────────────────────────────
# SYNONYM MAP
# Expand each word into a group of related terms.
# Add more as you encounter them.
# ─────────────────────────────────────────────
SYNONYMS = {
    "developer":  ["developer", "engineer", "programmer"],
    "engineer":   ["engineer", "developer", "programmer"],
    "frontend":   ["frontend", "front-end", "front end", "client-side"],
    "backend":    ["backend", "back-end", "back end", "server-side"],
    "fullstack":  ["fullstack", "full-stack", "full stack"],
    "software":   ["software", "application"],
    "web":        ["web", "website"],
    "react":      ["react", "reactjs", "react.js"],
    "node":       ["node", "nodejs", "node.js"],
    "python":     ["python"],
    "java":       ["java"],
    "mobile":     ["mobile", "android", "ios"],
    "devops":     ["devops", "dev ops", "infrastructure", "platform"],
    "cloud":      ["cloud", "aws", "azure", "gcp"],
}


def expand_keywords(keyword: str) -> list:
    """
    Takes a keyword phrase and returns all synonym variations.

    Example:
        "frontend developer" → 
        ["frontend", "front-end", "front end", "ui",
         "developer", "engineer", "programmer", "dev"]
    """
    expanded = set()
    words = keyword.lower().split()

    for word in words:
        if word in SYNONYMS:
            # Add all synonyms for this word
            expanded.update(SYNONYMS[word])
        else:
            # Word not in map — keep it as-is
            expanded.add(word)

    return list(expanded)

# Roles that should never appear in results regardless of keyword match
BLOCKED_TITLE_WORDS = [
    "sales", "marketing", "recruiter", "recruitment",
    "hr ", "human resources", "accountant", "finance",
    "legal", "operations manager", "office manager",
]

def is_blocked_title(title: str) -> bool:
    """Returns True if the title contains a word we never want."""
    title_lower = title.lower()
    return any(word in title_lower for word in BLOCKED_TITLE_WORDS)

def title_matches_keyword(title: str, keyword: str) -> bool:
    """
    Every word in the keyword must have at least one synonym match in the title.

    "frontend developer" → title must match something from BOTH:
        - ["frontend", "front-end", "front end", "ui"]   (for "frontend")
        - ["developer", "engineer", "programmer", "dev"] (for "developer")
    """
    title_lower = title.lower()
    words = keyword.lower().split()

    return all(
        any(term in title_lower for term in SYNONYMS.get(word, [word]))
        for word in words
    )


def get_job_listings(keywords: list, base_url: str, max_jobs: int = 5) -> list:
    """
    Searches a careers listing page for jobs matching given keywords.
    Uses synonym expansion so 'frontend developer' also matches
    'Frontend Engineer', 'UI Developer', 'Front-end Programmer' etc.
    """

    parsed = urlparse(base_url)
    domain_root = f"{parsed.scheme}://{parsed.netloc}"

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )
    }

    all_jobs = []

    for keyword in keywords:
        print(f"\n[SEARCHING] Keyword: '{keyword}'")
        print(f"[EXPANDED]  Matching against: {expand_keywords(keyword)}")

        search_url = f"{base_url}?keyword={keyword.replace(' ', '+')}"

        try:
            response = requests.get(search_url, headers=headers, timeout=10)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Could not fetch listing page: {e}")
            continue

        soup = BeautifulSoup(response.text, "html.parser")

        found = 0
        for tag_name in ["h2", "h3", "h4", "a"]:
            job_cards = soup.find_all(tag_name)

            for card in job_cards:
                # For <a> tags, use directly; for headings, find the <a> inside
                if tag_name == "a":
                    link_tag = card if card.get("href") else None
                else:
                    link_tag = card.find("a", href=True)

                if not link_tag:
                    continue

                title = link_tag.get_text(strip=True)
                if not title or len(title) < 5:  # skip empty or tiny links
                    continue

                href = link_tag.get("href", "")
                if not href:
                    continue

                # Build full URL
                if href.startswith("http"):
                    full_url = href
                elif href.startswith("/"):
                    full_url = domain_root + href
                else:
                    full_url = base_url.rstrip("/") + "/" + href

                # Skip duplicates
                if any(j["url"] == full_url for j in all_jobs):
                    continue

                # ✅ Synonym-aware matching
                if not title_matches_keyword(title, keyword):
                    continue

                # Skip blocked roles entirely
                if is_blocked_title(title):
                    print(f"  ✗ Blocked: '{title}'")
                    continue

                # Synonym-aware matching
                if not title_matches_keyword(title, keyword):
                    continue

                all_jobs.append({
                    "title": title,
                    "url": full_url,
                    "keyword_matched": keyword
                })

                found += 1
                print(f"  ✓ Matched: '{title}'")

                if found >= max_jobs:
                    break

            if found > 0:
                break

        if found == 0:
            print(f"  ✗ No matches found for '{keyword}' — try a broader keyword")

    return all_jobs


# Quick standalone test
if __name__ == "__main__":
    test_url = input("Paste the careers listing page URL: ").strip()
    keywords = input("Enter keywords (comma separated): ").strip().split(",")
    keywords = [k.strip() for k in keywords]

    jobs = get_job_listings(keywords=keywords, base_url=test_url, max_jobs=5)

    print(f"\n─── FOUND {len(jobs)} MATCHING JOB(S) ───")
    for i, job in enumerate(jobs, 1):
        print(f"\n{i}. {job['title']}")
        print(f"   {job['url']}")
        print(f"   Matched by: '{job['keyword_matched']}'")
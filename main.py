# main.py - The entry point that wires everything together
# Run with: python main.py

import sys
import os

# --------------------------------------------------------------------------------
# Make sure Python can find all our modules
# --------------------------------------------------------------------------------
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scraper.listing_scraper import get_job_listings
from scraper.static_scraper import scrape_job_page
from ai.cover_letter_gen import generate_cover_letter_sections
from documents.docx_handler import read_template, replace_placeholders, save_cover_letter
from tracker.job_tracker import save_to_tracker
from config import (
    TEMPLATE_PATH,
    OUTPUT_DIR,
    JOB_KEYWORDS,
    MAX_JOBS_PER_KEYWORD,
    YOUR_NAME,
)

KEYWORD_SEARCH = 1
DIRECT_URL = 2
MANUAL_ENTRY = 3
EXIT_PROGRAM = 4
VALID_INPUT = [1, 2, 3, 4]

def ask_required(prompt: str, field_name: str) -> str:
    """
    Keeps asking until the user types something non-empty.
    """
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print(f"[!] {field_name} cannot be empty. Please try again.")

# --------------------------------------------------------------------------------
# HELPERS
# --------------------------------------------------------------------------------

def print_banner():
    print("""
=================================================
||        AI Job Application Agent             ||
||        Running 100% locally with Ollama     ||
=================================================
    """)

def ask_company_name(suggested: str = "") -> str:
    """Ask the user to confirm or enter the company name."""
    if suggested:
        answer = input(f"\nCompany name detected as '{suggested}'. Press Enter to confirm or type a new name: ").strip()
        # If they just hit Enter, use the suggestion - that's valid
        return answer if answer else suggested

    # No suggestion - must type something
    return ask_required("Enter the company name: ", "Company name")

def pick_job_from_list(jobs: list) -> dict | None:
    """Show numbered job list and let user pick one."""
    if not jobs:
        print("\n[!] No matching jobs found. Try different keywords.")
        return None

    print(f"\n{'--'*50}")
    print(f"  Found {len(jobs)} matching job(s):")
    print(f"{'--'*50}")

    for i, job in enumerate(jobs, 1):
        print(f"  {i}. {job['title']}")
        print(f"     {job['url']}")
        print()

    while True:
        choice = input("Enter the number of the job you want to apply for (or 0 to cancel): ").strip()
        if choice == "0":
            return None
        if choice.isdigit() and 1 <= int(choice) <= len(jobs):
            return jobs[int(choice) - 1]
        print("[!] Invalid choice. Please enter a number from the list.")


def extract_company_from_url(url: str) -> str:
    """
    Best-effort company name extraction from URL.
    e.g. https://careers.company.com/... → 'company'
    """
    try:
        domain = url.split("//")[-1].split("/")[0]  # e.g. careers.company.com
        parts = domain.split(".")
        # Filter out common non-name parts
        ignore = {"careers", "jobs", "work", "www", "com", "fi", "io", "co", "uk"}
        name_parts = [p for p in parts if p.lower() not in ignore]
        return name_parts[0].capitalize() if name_parts else ""
    except Exception:
        return ""

def get_job_details_manually() -> dict:
    print("\n-- MANUAL JOB INPUT -----------------")
    print("--------------------------------------------------------------------------------\n")

    # Both required
    job_title = ask_required("Job title (copy from the listing): ", "Job title")
    company_name = ask_required("Company name: ", "Company name")

    print("\nPaste the full job description below.")
    print("When done, type END on a new line and press Enter:\n")

    # Description also required
    while True:
        lines = []
        while True:
            line = input()
            if line.strip().upper() == "END":
                break
            lines.append(line)

        job_description = "\n".join(lines).strip()

        if job_description:
            break
        print("[!] Job description cannot be empty. Please paste the description and type END again.\n")

    return {
        "title": job_title,
        "description": job_description,
        "url": "manual-entry",
        "company": company_name
    }

def run_full_pipeline(job_url: str, company_name: str):
    """Scrapes a URL then runs the pipeline. Use for Options 1 and 2."""

    print(f"\n[1/4] Scraping job page...")
    job_data = scrape_job_page(job_url)

    if not job_data:
        print("[ERROR] Could not scrape the job page.")
        print("[HINT] If this is a LinkedIn URL, use Option 3 instead.")
        return

    run_full_pipeline_from_data(job_data, company_name)


def run_full_pipeline_from_data(job_data: dict, company_name: str, entry_type_manual: bool = False):
    """
    Runs steps 2-4 on already-collected job data.
    Called by both the URL scraper and the manual input option.
    """

    job_title = job_data.get("title", "Unknown Role")
    job_description = job_data.get("description", "")

    print(f"  ✓ Title: {job_title}")
    print(f"  ✓ Description: {len(job_description)} characters")

    print()

    if not entry_type_manual:
        # -- Let user confirm or edit the job title -------------------
        edited_title = input(
            f"Job title detected as '{job_title}'.\n"
            f"Press Enter to confirm or type a new job title: "
        ).strip()

        if edited_title:
            job_title = edited_title
            print(f"  ✓ Using: '{job_title}'")

    if not job_description:
        print("[WARNING] Description is empty - cover letter may be generic.")

    # -- Step 2: AI generation ----------------------------------------------
    print(f"\n[2/4] Generating cover letter with Ollama (~20-40 seconds)...")

    try:
        replacements = generate_cover_letter_sections(
            job_title=job_title,
            job_description=job_description,
            company_name=company_name,
        )
    except Exception as e:
        print(f"\n[ERROR] Ollama failed: {e}")
        print("[HINT] Run 'ollama serve' in a separate terminal.")
        return

    # -- Step 3: Fill template ----------------------------
    print(f"\n[3/4] Filling your cover letter template...")

    try:
        doc = read_template(TEMPLATE_PATH)
    except FileNotFoundError as e:
        print(f"[ERROR] {e}")
        print(f"[HINT] Place your template at: {TEMPLATE_PATH}")
        return

    filled_doc = replace_placeholders(doc, replacements)

    # -- Step 4: Save ----------------------
    print(f"\n[4/4] Saving cover letter...")
    output_path = save_cover_letter(filled_doc, job_title, company_name, OUTPUT_DIR)

    print(f"""
        {'═'*50}
        ✅ Cover letter ready!
        📄 File: {output_path}
        🏢 Company: {company_name}
        💼 Role: {job_title}
        {'═'*50}
    """)

    print("\n-- SKILLS MATCH --")
    print(replacements.get("{{SKILLS_MATCH_SENTENCE}}", ""))
    print("\n-- COMPANY PARAGRAPH --")
    print(replacements.get("{{COMPANY_PARAGRAPH}}", ""))

    # -- Tracker prompt ----------------------------------------------
    print()
    log_it = input("Log this application to your job tracker? (y/n): ").strip().lower()

    if log_it == "y":
        success = save_to_tracker(
            company=company_name,
            job_role=job_title,
            job_description=job_description,
        )
    else:
        print("[TRACKER] Skipped - you can log it manually later.")

# --------------------------------------------------------------------------------
# MAIN MENU
# --------------------------------------------------------------------------------

def main():
    print_banner()
    print(f"  Logged in as: {YOUR_NAME}")
    print(f"  Template: {TEMPLATE_PATH}")
    print(f"  Output folder: {OUTPUT_DIR}/\n")

    print("How would you like to find a job?")
    print("  1. Search by keyword (uses your config.py keywords)")
    print("  2. Paste a direct job URL")
    print("  3. Paste job details manually")
    print("  4. Exit")

    while True:
        try:
            choice = int(input("\nEnter 1, 2, 3 or 4: ").strip())
            if choice in VALID_INPUT:
                break
            print("Invalid input. Please enter 1, 2, 3 or 4.")
        except ValueError:
            print("Invalid input. Please enter a valid number between 1, 2, 3 or 4.")

    # -- Option 1: Keyword search ----------------------------------------------
    if choice == KEYWORD_SEARCH:
        print(f"\n[INFO] Searching with keywords from config.py: {JOB_KEYWORDS}")
        custom = input("Press Enter to use these, or type your own (comma separated): ").strip()
        keywords = [k.strip() for k in custom.split(",")] if custom else JOB_KEYWORDS

        # Listing URL is required
        target_url = ask_required("\nPaste the careers listing page URL: ", "Careers page URL")

        jobs = get_job_listings(
            keywords=keywords,
            base_url=target_url,
            max_jobs=MAX_JOBS_PER_KEYWORD
        )

        if not jobs:
            print("\n[INFO] No jobs found with static scraper.")
            use_selenium = input("Try again with Firefox/Selenium? (y/n): ").strip().lower()

            if use_selenium == "y":
                from scraper.dynamic_scraper import scrape_listing_page_dynamic
                jobs = scrape_listing_page_dynamic(
                    base_url=target_url,
                    keywords=keywords,
                    max_jobs=MAX_JOBS_PER_KEYWORD
                )

        selected_job = pick_job_from_list(jobs)
        if not selected_job:
            print("No job selected. Exiting.")
            return

        suggested_company = extract_company_from_url(target_url)
        company_name = ask_company_name(suggested_company)

        run_full_pipeline(selected_job["url"], company_name)

    # -- Option 2: Direct URL -------------------------------
    elif choice == DIRECT_URL:
        # URL is required
        job_url = ask_required("\nPaste the job listing URL: ", "Job URL")

        suggested_company = extract_company_from_url(job_url)
        company_name = ask_company_name(suggested_company)

        run_full_pipeline(job_url, company_name)
    
    # -- Option 3: Enter job description manually -------------------
    elif choice == MANUAL_ENTRY:
        job_data = get_job_details_manually()

        run_full_pipeline_from_data(
            job_data=job_data,
            company_name=job_data["company"],
            entry_type_manual=True
        )

    # -- Option 4: Exit ------------------------
    elif choice == EXIT_PROGRAM:
        print("Goodbye!")

    else:
        print("[!] Invalid choice. Run the program again.")


if __name__ == "__main__":
    main()

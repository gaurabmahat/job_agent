# 🤖 AI Job Application Agent

A local Python tool that scrapes job listings, matches them to your skills, generates custom tailored cover letters, and tracks your applications - running 100% on local machine with no paid APIs.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)
![Ollama](https://img.shields.io/badge/Ollama-Llama%203.2-black?style=flat)
![BeautifulSoup](https://img.shields.io/badge/BeautifulSoup4-scraping-green?style=flat)
![python-docx](https://img.shields.io/badge/python--docx-Word%20output-blue?style=flat)
![openpyxl](https://img.shields.io/badge/openpyxl-Job%20tracker-217346?style=flat)
![License](https://img.shields.io/badge/license-MIT-brightgreen?style=flat)

---

## Table of Contents

- [Demo](#demo)
- [Features](#features)
- [How It Works](#how-it-works)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Common Errors and Solutions](#common-errors-and-solutions)
- [Limitations](#limitations)
- [Future Improvements](#future-improvements)
- [Author's Note](#authors-note)

---

## Demo

```
╔══════════════════════════════════════════════╗
║        AI Job Application Agent              ║
║        Running 100% locally with Ollama      ║
╚══════════════════════════════════════════════╝

    Logged in as: {user_name}

How would you like to find a job?
    1. Search by keyword on a careers page
    2. Paste a direct job URL
    3. Paste job details manually
    4. Exit

Enter 1, 2, 3 or 4: 2

Paste the job listing URL: https://careers.company.com/en/find-jobs/r06123-...

Company name detected as 'company'. Press Enter to confirm or type a new name:

Job title detected as 'Software Developer (NodesJs, React) - Trademark Listings'.
Press Enter to confirm or type a new job title: Software Developer

[1/4] Scraping job page...
    ✓ Title: Software Developer
    ✓ Description: 2847 characters extracted

[2/4] Generating cover letter with Ollama (~20-40 seconds)...
[AI] Matching your skills to job requirements...
[AI] Writing company paragraph for Company...
[AI] Done.

[3/4] Filling your cover letter template...
[4/4] Saving cover letter...

══════════════════════════════════════════════════
  ✅ Cover letter ready!
  📄 File: output/CoverLetter_company_Software_Developer_date.docx
  🏢 Company: company
  💼 Role: Software Developer
══════════════════════════════════════════════════

Log this application to your job tracker? (y/n): y
[TRACKER] Saved to tracker: job_tracker.xlsx
[TRACKER] You have 3 application(s) logged in job_tracker.xlsx

```

## Features

- **Keyword-based job search** - searches any careers listing page for roles matching your keywords
- **Synonym-aware matching** - "frontend developer" also matches "Frontend Engineer", "UI Developer" and similar titles
- **Role blocklist** - automatically filters out irrelevant roles
- **Direct URL scraping** - paste a specific job URL and it extracts the title and description automatically
- **Manual paste fallback** - for sites like LinkedIn that block scrapers, paste the description yourself
- **Local AI generation** - Ollama + Llama 3.2 writes two tailored paragraphs per application
- **Hybrid cover letter strategy** - your fixed experience sections stay locked; only job-specific content is AI-generated
- **Unique timestamped filenames** - every output file has a timestamp to the second, so you never overwrite a previous letter
- **Word document output** - generates a ready-to-review '.docx' file
- **Job application tracker** - optionally logs each application to 'job_tracker.xlsx' with company, role, description, and date
- **Zero data leakage** - nothing leaves your machine; no external API calls for generation
- **Private config** - personal data lives in '.env'

---

## How It Works

```
User input (URL, keywords, or manual paste)
                ↓
    ┌───────────────────────────┐
    │   listing_scraper.py      │  Finds matching job URLs from a careers page
    │                           │  Synonym expansion + role blocklist filtering
    └───────────────────────────┘
                ↓
    ┌───────────────────────────┐
    │   static_scraper.py       │  Extracts job title + description from a page
    └───────────────────────────┘
                ↓
    ┌───────────────────────────┐
    │   cover_letter_gen.py     │  Sends job data to local Ollama LLM
    │   (Ollama + Llama 3.2)    │  Returns two tailored paragraphs
    └───────────────────────────┘
                ↓
    ┌───────────────────────────┐
    │   docx_handler.py         │  Reads your .docx template
    │                           │  Replaces {{PLACEHOLDERS}} with content
    │                           │  Saves to output/ 
    └───────────────────────────┘
                ↓
    ┌───────────────────────────┐
    │   job_tracker.py          │  Logs application to Excel
    │   (optional)              │  
    └───────────────────────────┘
                ↓
        output/CoverLetter_Company_Role_Date.docx
        job_tracker.xlsx  (if you chose to log it)

```

**Cover letter placeholder map:**

| Placeholder | Source | Changes per job? |
|---|---|---|
| '{{JOB_TITLE}}' | Scraped + confirmed by user | ✅ Yes |
| '{{COMPANY_NAME}}' | Detected + confirmed by user | ✅ Yes |
| '{{SKILLS_MATCH_SENTENCE}}' | AI - matches your skills to job requirements | ✅ Yes |
| '{{COMPANY_PARAGRAPH}}' | AI - why you want this specific role | ✅ Yes |
| Everything else | Your fixed template text | 🔒 Never |

---

## Tech Stack

| Tool | Purpose | Why I chose it |
|---|---|---|
| [Ollama](https://ollama.com) + Llama 3.2 | Local LLM for text generation | Runs offline, fits in RAM on mid-range hardware, no API cost |
| [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/) | HTML parsing and scraping | Lightweight, readable - right tool for static pages |
| [Requests](https://requests.readthedocs.io) | HTTP requests | Simple and reliable for fetching pages |
| [python-docx](https://python-docx.readthedocs.io) | Read/write '.docx' files | Handles Word format without needing Word installed |
| [openpyxl](https://openpyxl.readthedocs.io) | Read/write '.xlsx' tracker | Reliable Excel handling with formatting support |
| [python-dotenv](https://github.com/theskumar/python-dotenv) | Load '.env' config | Keeps personal data out of the codebase |
| Python 3.10+ | Core language | Standard, cross-platform |

---

## Installation

### Prerequisites

- Python 3.10 or higher
- [Ollama](https://ollama.com) installed on your machine
- Git

### Step 1 - Clone the repo

``` bash
git clone https://github.com/gaurabmahat/job-agent.git
cd job-agent
```

### Step 2 - Create and activate a virtual environment

```bash
#Windows (PowerShell)
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3 - Install dependencies

```bash
pip install -r requirements.txt
```

### Step 4 - Install and set up Ollama

1. Download Ollama from [ollama.com](https://ollama.com) and install it
2. Pull the Llama 3.2 model:

```bash
ollama pull llama3.2
```

3. Test it works:

```bash
ollama run llama3.2 "Say hello in one sentence"
```

### Step 5 - Set up your configuration

```bash
# Windows (PowerShell)
copy .env.example .env

# macOS / Linux
cp .env.example .env
```

Open '.env' and fill in your details (see [Configuration](#configuration) below).

### Step 6 - Add your cover letter template

1. Read 'cover_letter_template_guide.txt' for full instructions
2. Create 'template/cover_letter.docx' following the guide 
3. Add these placeholders in your word document where appropriate:
    - '{{JOB_TITLE}}'
    - '{{COMPANY_NAME}}'
    - '{{SKILLS_MATCH_SENTENCE}}'
    - '{{COMPANY_PARAGRAPH}}'

---

## Configuration

This project uses a '.env' file for all personal data.

Copy '.env.example' to '.env' and fill in your details.

```bash
# Personal info
YOUR_NAME=Your Full Name
YOUR_EMAIL=your.email@example.com
YOUR_PHONE=+1234567890
YOUR_LOCATION=Your City, Country
YOUR_PORTFOLIO=your-portfolio.com
YOUR_GITHUB=github.com/yourusername
YOUR_LINKEDIN=linkedin.com/in/yourprofile

# Job search
JOB_KEYWORDS=software developer,frontend developer,full stack developer
MAX_JOBS_PER_KEYWORD=5

# AI model
OLLAMA_MODEL=llama3.2

# Your skills (used for skills matching)
YOUR_SKILLS=write your skills here

#Your background 
YOUR_BACKGROUND=write your background here

```

---

## Usage

Always start Ollama in a separate terminal before running the tool:

```bash
ollama serve
```

Then run the agent:

```bash
python main.py
```

### Option 1 - Search by keyword on a careers page

```
Enter 1, 2, 3 or 4: 1

Keywords from config.py: ['software developer', 'frontend developer', ...]
Press Enter to use these, or type your own (comma separated): react developer

Paste the careers listing page URL: https://careers.company.com/en/find-jobs/

[SEARCHING] Keyword: 'react developer'
[EXPANDED]  Matching against: ['react', 'reactjs', 'developer', 'engineer', ...]

──────────────────────────────────────────────────
  Found 2 matching job(s):
──────────────────────────────────────────────────
  1. Software Developer (NodeJS, React, TypeScript)
     https://careers.company.com/en/find-jobs/r0625/...

  2. Frontend Developer - React
     https://careers.company.com/en/find-jobs/r0624/...

Enter the number of the job you want to apply for (or 0 to cancel): 1
```

### Option 2 - Direct job URL

```
Enter 1, 2, 3 or 4: 2

Paste the job listing URL: https://careers.company.com/jobs/12345

Company name detected as 'Company'. Press Enter to confirm or type a new name:

Job title detected as 'Software Developer (NodeJS, React) - Updated'.
Press Enter to confirm or type a new job title: Software Developer
```

### Option 3 - Manual paste

```
Enter 1, 2, 3 or 4: 3

── MANUAL JOB INPUT ──────────────────────────
Job title (copy from the listing): Software Developer
Company name: Company

Paste the full job description below.
When done, type END on a new line and press Enter:

We are looking for a Software Developer with experience in...
[paste full description]
END
```

### Option 4 - Exit program

```
Enter 1, 2, 3 or 4: 4
Goodbye!
```

### Job Tracker 

At the end of every successful run you'll be asked:

```
Log this application to your job tracker? (y/n): y
[TRACKER] Saved to tracker: job_tracker.xlsx
[TRACKER] You have 3 application(s) logged in job_tracker.xlsx
```

'job_tracker.xlsx' is created automatically on first use and appended to on every subsequent save - it never overwrites existing entries. Open it in Excel anytime to review your full application history.

---

## Common Errors and Solutions

These are real errors I encountered during development and testing.

| Error | Cause | Fix |
|---|---|---|
| 'ModuleNotFoundError: No module named 'documents'' | Running a file from inside a subfolder | Always run from the project root: 'python main.py' |
| 'ConnectionError' from Ollama | Ollama service isn't running | Open a separate terminal and run 'ollama serve' before starting the agent |
| Empty job description scraped | Site uses JavaScript rendering or unusual CSS classes | Use Option 3 (manual paste) for these sites |
| Irrelevant jobs in search results | Keyword too broad (e.g. "engineer" matching "Sales Engineer") | Add the role type to 'BLOCKED_TITLE_WORDS' in 'listing_scraper.py' |
| Placeholder not replaced in output | Placeholder misspelled in '.docx' template | Check spelling - must be exactly '{{PLACEHOLDER_NAME}}' with double curly braces, no spaces |
| 'EnvironmentError: Missing required variable' | '.env' file is missing a required key | Open '.env' and add the missing variable - the error message tells you which one |
| 'FileNotFoundError' for template | 'templates/cover_letter.docx' doesn't exist | Create the file - see 'cover_letter_template_guide.txt' for instructions |
| 0 jobs found with keyword search | Site renders listings with JavaScript | Use Option 2 (direct URL) or Option 3 (manual paste) |
| 'PermissionError' when saving '.docx' | Output file is open in Word | Close the file in Word and press Enter - the tool retries automatically |
| 'PermissionError' when saving '.xlsx' | Tracker file is open in Excel | Close the file in Excel and press Enter - the tool retries automatically |

---

## Limitations

**What this tool can and can't do:**

- **LinkedIn is not scrapeable** - LinkedIn actively blocks automated access. Use Option 3 (manual paste) for LinkedIn jobs. This is a deliberate design decision, not a bug to be fixed.
- **JavaScript-heavy job boards** - Sites that load job listings dynamically (Indeed, Glassdoor) may return empty results with the current scraper. Option 3 works as a fallback. Selenium support is planned.
- **CSS selector fragility** - The scraper uses a prioritised list of common CSS class names. Unusual career page designs may need a custom selector added to 'candidate_selectors' in 'static_scraper.py'.
- **AI output needs review** - The generated paragraphs are a starting point. Always read the output before submitting an application. The model can occasionally misread a job description or produce an awkward sentence.
- **One cover letter format** - The tool is built around a single '.docx' template. Multiple template support is a future improvement.
- **Windows-tested** - Developed and tested on Windows. Should work on macOS and Linux but not tested there yet.

---

## Future Improvements

- [ ] Selenium integration for JavaScript-rendered listing and job pages
- [ ] Streamlit web UI - visual interface instead of CLI
- [ ] Multiple template support - different letters for frontend vs backend roles
- [ ] Better description parsing - handle unstructured job descriptions more reliably
- [ ] 'robots.txt' checker - automated check before scraping any URL

---

## Author's Note

I used Claude as a coding assistant when building this project. It helped me generate initial boilerplate and suggested implementation patterns. All key decisions, debugging, edge case handling, and prompt engineering were done by me.

The cover letter strategy - locking 80% as fixed text and only generating the job-specific paragraphs - was a deliberate design decision I made after thinking about what actually makes a cover letter good.

---

## License

MIT - Feel free to do what you want with it, just don't blame me if it gets your a job at a company you don't want. 

---

*[LinkedIn](https://linkedin.com/in/gaurab-mahat-937299191/) · [GitHub](https://github.com/gaurabmahat)*



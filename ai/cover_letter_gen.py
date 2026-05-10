import ollama
from config import OLLAMA_MODEL, YOUR_SKILLS

def generate_cover_letter_sections(
    job_title: str,
    job_description: str,
    company_name: str,
    your_background: str,
) -> dict:
    """
    Generates two targeted sections:
    1. A skills match sentence — mirrors job requirements with candidate's real skills
    2. A company paragraph — explains genuine interest in this specific role
    """

    # ── Skills match ────────────────────────────────────────────────────────────

    print(f"[AI] Matching your skills to job requirements...")

    skills_prompt = f"""
        You are helping a software developer tailor one sentence of their cover letter.

        Job Title: {job_title}
        Company: {company_name}
        Job Description: {job_description[:1000]}

        Candidate's actual skills (only use skills from this list — never invent skills):
        {YOUR_SKILLS}

        Write ONE sentence (max 45 words) that:
        - Identifies 2-4 skills from the candidate's list that directly match the job description
        - Connects those skills to what this specific role needs
        - Sounds natural and confident, not like a template
        - Write as if a confident, experienced developer wrote this themselves, not an AI
        - Varies the opening freely

        Here are example STYLES to draw from (do not copy these, just use them
        as inspiration for tone and structure — write something fresh each time):
        * "My hands-on work with React and TypeScript maps closely to..."
        * "Having built RESTful APIs and worked with Azure DevOps daily, I'm well placed to..."
        * "The stack you're working with — NodeJS, React, and AWS — closely mirrors..."
        * "Working with {company_name}'s tech stack would feel familiar from day one, given my..."

        Output only the sentence, nothing else. No explanation, no preamble.
    """

    # ── Company paragraph ────────────────────────────────────────────────────────

    print(f"[AI] Writing company paragraph for {company_name}...")

    company_prompt = f"""
        You are helping a software developer write one paragraph of a cover letter.

        Job Title: {job_title}
        Company: {company_name}
        Job Description: {job_description[:1000]}

        Candidate background summary:
        {your_background}

        Write ONE paragraph (3-4 sentences) that:
        - Explains why the candidate is genuinely interested in THIS specific role and company
        - References something concrete from the job description (tech stack, mission, team structure, or product)
        - Connects the candidate's background to what this company works on
        - Sounds genuine and human, not like a template
        - Does NOT repeat skills already listed elsewhere in the letter
        - Is under 100 words
        - Varies the opening freely

        Here are example OPENING STYLES to inspire variety
        (do not copy these — write something fresh and specific each time):
        * "The opportunity to work on [specific thing from job description]..."
        * "{company_name}'s focus on [something from job description] is what caught my attention..."
        * "Having worked in [relevant context], I find {company_name}'s approach to [X] particularly compelling..."
        * "Systems that [do what this company does] are exactly the kind of work I want to grow in..."
        * "Joining a team that [specific detail from job description] aligns well with where I want to take my career..."

        Output only the paragraph text, nothing else.
    """

    # ── Call Ollama ──────────────────────────────────────────────────────────────

    def ask_ollama(prompt: str, label: str) -> str:
        try:
            response = ollama.chat(
                model=OLLAMA_MODEL,
                messages=[{"role": "user", "content": prompt}]
            )
            return response["message"]["content"].strip()
        except Exception as e:
            print(f"[ERROR] Ollama failed on '{label}': {e}")
            print("[HINT] Make sure Ollama is running: ollama serve")
            return ""

    skills_sentence = ask_ollama(skills_prompt, "skills match")
    company_paragraph = ask_ollama(company_prompt, "company paragraph")

    # ── Fallbacks if Ollama fails ────────────────────────────────────────────────

    if not skills_sentence:
        skills_sentence = (
            "In particular, my experience with React, TypeScript, and Node.js "
            "aligns with the technical requirements of this role."
        )

    if not company_paragraph:
        company_paragraph = (
            f"What draws me to {company_name} is the opportunity to contribute "
            f"to meaningful work in a collaborative environment while growing as a developer."
        )

    print("[AI] Done.")

    return {
        "{{JOB_TITLE}}":             job_title,
        "{{COMPANY_NAME}}":          company_name,
        "{{SKILLS_MATCH_SENTENCE}}": skills_sentence,
        "{{COMPANY_PARAGRAPH}}":     company_paragraph,
    }
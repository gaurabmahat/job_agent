from docx import Document
import os
from datetime import datetime

def read_template(template_path: str) -> Document:
    """
    Opens the .docx template and returns a Document object.
    """
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Template not found at: {template_path}")
    
    return Document(template_path)


def replace_placeholders(doc: Document, replacements: dict) -> Document:
    """
    Replaces placeholder tags in the document with actual content.
    Handles text that may be split across multiple 'runs' inside a paragraph.
    
    replacements = {
        "{{JOB_TITLE}}": "Software Developer",
        "{{COMPANY_NAME}}": "COMPANY",
        ...
    }
    """

    for paragraph in doc.paragraphs:
        for placeholder, value in replacements.items():

            # First check if the whole paragraph text contains the placeholder
            if placeholder in paragraph.text:

                # Word sometimes splits one word across multiple 'runs' (XML elements)
                # e.g. "{{JOB" in run 1, "_TITLE}}" in run 2
                # We need to consolidate the paragraph text, then rewrite it
                
                full_text = "".join(run.text for run in paragraph.runs)

                if placeholder in full_text:
                    new_text = full_text.replace(placeholder, value)

                    # Clear all runs and put the new text in the first one
                    # This preserves the paragraph's formatting (font, size, etc.)
                    for i, run in enumerate(paragraph.runs):
                        if i == 0:
                            run.text = new_text
                        else:
                            run.text = ""  # Empty out the other runs

    return doc


def save_cover_letter(doc: Document, job_title: str, company_name: str, output_dir: str = "output") -> str:
    """
    Saves the filled cover letter to the output folder.
    Returns the path of the saved file.
    """

    # Create output folder if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Build a clean filename: "CoverLetter_COMPANY_SoftwareDeveloper_2025-01-15.docx"
    clean_title = job_title.replace(" ", "_").replace("/", "-")[:30]  # limit length
    clean_company = company_name.replace(" ", "_")[:20]
    # Timestamp with seconds - guarantees a unique filename every run
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    filename = f"CoverLetter_{clean_company}_{clean_title}_{timestamp}.docx"
    output_path = os.path.join(output_dir, filename)

    try:
        doc.save(output_path)
        print(f"[SAVED] Cover letter saved to: {output_path}")
    except PermissionError:
        print(f"\n[ERROR] Could not save - the file is open in Word.")
        print(f"[FIX]   Close the file in Word and press Enter to try again...")
        input()  # Wait for user to close Word
        try:
            doc.save(output_path)
            print(f"[SAVED] Saved successfully: {output_path}")
        except PermissionError:
            # Last resort - add extra timestamp to avoid any conflict
            fallback_path = output_path.replace(".docx", "_v2.docx")
            doc.save(fallback_path)
            print(f"[SAVED] Saved as fallback: {fallback_path}")
    return output_path


# Quick test
if __name__ == "__main__":
    from docx_handler import read_template, replace_placeholders, save_cover_letter

    template = read_template("templates/cover_letter.docx")

    # Fake replacements just to test the mechanism
    test_replacements = {
        "{{JOB_TITLE}}": "Software Developer",
        "{{COMPANY_NAME}}": "COMPANY",
        "{{OPENING_PARAGRAPH}}": "I am excited to apply for this role.",
        "{{SKILLS_PARAGRAPH}}": "I have 3 years of experience with NodeJS and React.",
        "{{CLOSING_PARAGRAPH}}": "I look forward to hearing from you."
    }

    filled_doc = replace_placeholders(template, test_replacements)
    save_cover_letter(filled_doc, "Software Developer", "COMPANY")
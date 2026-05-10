# config.py — reads all private data from .env

import os
from dotenv import load_dotenv

# Load .env file from project root
load_dotenv()

def get_required(key: str) -> str:
  """
  Reads a required variable from .env.
  Crashes with a clear message if it's missing.
  """
  value = os.getenv(key)
  if not value:
      raise EnvironmentError(
          f"\n[ERROR] Missing required variable '{key}' in your .env file.\n"
          f"[FIX]   Open .env and add: {key}=your_value_here\n"
          f"[HINT]  Use .env.example as a reference.\n"
      )
  return value

# ─────────────────────────────────────────────
# PATHS
# ─────────────────────────────────────────────
TEMPLATE_PATH = "templates/cover_letter.docx"
OUTPUT_DIR = "output"

# ─────────────────────────────────────────────
# PERSONAL INFO
# ─────────────────────────────────────────────
YOUR_NAME       = get_required("YOUR_NAME")
YOUR_LOCATION   = get_required("YOUR_LOCATION")
YOUR_EMAIL      = get_required("YOUR_EMAIL")
YOUR_PHONE      = get_required("YOUR_PHONE")
YOUR_PORTFOLIO  = get_required("YOUR_PORTFOLIO")
YOUR_GITHUB     = get_required("YOUR_GITHUB")
YOUR_LINKEDIN   = get_required("YOUR_LINKEDIN")

# ─────────────────────────────────────────────
# JOB SEARCH SETTINGS
# ─────────────────────────────────────────────

# Stored as comma-separated string in .env → converted to list here
JOB_KEYWORDS = [
  k.strip()
  for k in get_required("JOB_KEYWORDS").split(",")
  if k.strip()
]

MAX_JOBS_PER_KEYWORD = int(os.getenv("MAX_JOBS_PER_KEYWORD", "5"))

# ─────────────────────────────────────────────
# AI SETTINGS
# ─────────────────────────────────────────────
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")

# ─────────────────────────────────────────────
# YOUR PROFILE — fed to Ollama for generation
# ─────────────────────────────────────────────
YOUR_SKILLS     = get_required("YOUR_SKILLS")
YOUR_BACKGROUND = get_required("YOUR_BACKGROUND")

# Quick Test
if __name__ == "__main__":
  print(f"Loaded config for: {YOUR_NAME}")
  print(f"Keywords: {JOB_KEYWORDS}")
  print(f"Model: {OLLAMA_MODEL}")
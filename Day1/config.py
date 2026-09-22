"""Shared configuration: chooses the LLM provider and holds the private data."""
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()  # reads the .env file in this folder

PROVIDER = os.getenv("PROVIDER", "ollama").strip().lower()

if PROVIDER == "ollama":  # Option A: local model, no key
    BASE_URL = "http://localhost:11434/v1"
    API_KEY = "ollama"  # any text works for Ollama
    MODEL = os.getenv("MODEL", "qwen2.5:1.5b")
elif PROVIDER == "groq":  # Option B: free cloud key
    BASE_URL = "https://api.groq.com/openai/v1"
    API_KEY = os.getenv("GROQ_API_KEY")
    MODEL = os.getenv("MODEL", "openai/gpt-oss-20b")
elif PROVIDER == "huggingface":  # Option C: free cloud key
    BASE_URL = "https://router.huggingface.co/v1"
    API_KEY = os.getenv("HF_TOKEN")
    MODEL = os.getenv("MODEL", "openai/gpt-oss-20b")
else:
    raise SystemExit(f"Unknown PROVIDER '{PROVIDER}'. Use ollama, groq or huggingface.")

if not API_KEY:
    raise SystemExit(f"No API key found for PROVIDER={PROVIDER}. Check your .env file.")

client = OpenAI(base_url=BASE_URL, api_key=API_KEY)

# --- Private-data scenario: Academic Status Assistant -----------------
# Attendance % and internal marks for a small set of students. No public
# LLM has ever seen this data -- it lives only in this dictionary.
ATTENDANCE = {
    "CS137": 71,   # below 75% condonation limit
    "CS101": 88,
    "CS210": 79,
}

INTERNAL_MARKS = {
    ("CS137", "DBMS"): 22,
    ("CS137", "COMPUTER_NETWORKS"): 24,
    ("CS101", "DBMS"): 27,
}

QUESTIONS = [
    "What is my attendance percentage for roll number CS137?",
    "What is my total internal mark for DBMS and COMPUTER_NETWORKS for CS137 after adding 2 bonus marks?",
    "Is CS137's attendance below the 75% condonation limit, and by how much?",
    "Write a two-line motivational message for exam week.",
]


def banner(system_name):
    print(f"\n=== {system_name} | provider: {PROVIDER} | model: {MODEL} ===\n")

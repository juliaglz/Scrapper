import os
import sys
import tempfile
import subprocess
import json
from pydantic import BaseModel
from bs4 import BeautifulSoup
import requests
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise RuntimeError("Define the environment variable OPENROUTER_API_KEY in .env")

class ScrapeRequest(BaseModel):
    url: str
    instruction: str

def clean_code(code: str) -> str:
    """Remove markdown or ```python blocks."""
    if code.startswith("```") and code.endswith("```"):
        code = code.strip("`").strip()
        if code.startswith("python"):
            code = code[len("python"):].strip()
    return code

# --- Simple requests + BS4 method ---
def fetch_page_simple(url: str) -> str:
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                             "AppleWebKit/537.36 (KHTML, like Gecko) "
                             "Chrome/115.0.0.0 Safari/537.36"}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
    except Exception as e:
        raise RuntimeError(f"Error downloading page: {e}")

    soup = BeautifulSoup(resp.text, "html.parser")
    elements = []
    for tag in soup.find_all(True)[:200]:
        desc = tag.name
        if tag.get("id"):
            desc += f"#{tag['id']}"
        if tag.get("class"):
            desc += "." + ".".join(tag["class"])
        elements.append(desc)
    return "\n".join(elements)

# --- Playwright fallback method ---
def fetch_page_playwright(url: str) -> str:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)
        html = page.content()
        browser.close()

    soup = BeautifulSoup(html, "html.parser")
    elements = []
    for tag in soup.find_all(True)[:200]:
        desc = tag.name
        if tag.get("id"):
            desc += f"#{tag['id']}"
        if tag.get("class"):
            desc += "." + ".".join(tag["class"])
        elements.append(desc)
    return "\n".join(elements)

# --- Generate scraper code via LLM ---
def generate_scraper_code(url: str, instruction: str, structure: str) -> str:
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    prompt = [
        {"role": "system",
         "content": "You are an expert Python web scraper. Generate only valid Python code with requests and BeautifulSoup. Output must be JSON. No explanations or markdown."},
        {"role": "user",
         "content": f"URL: {url}\nStructure:\n{structure}\nInstruction: {instruction}"}
    ]
    payload = {
        "model": "openai/gpt-4o-mini",
        "messages": prompt,
        "temperature": 0,
        "max_tokens": 800
    }
    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
    response.raise_for_status()
    return clean_code(response.json()["choices"][0]["message"]["content"])

# --- Main scraper function with fallback ---
def run_scraper(request: ScrapeRequest):
    try:
        structure = fetch_page_simple(request.url)
    except Exception as e:
        print(f"Simple method failed, falling back to Playwright: {e}")
        structure = fetch_page_playwright(request.url)

    code = generate_scraper_code(request.url, request.instruction, structure)

    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as tmp:
        tmp.write(code)
        tmp.flush()

        proc = subprocess.run(
            [sys.executable, tmp.name],
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=30
        )

    if proc.returncode != 0:
        raise RuntimeError(f"Error running scraper: {proc.stderr}")

    data = json.loads(proc.stdout)
    return {"data": data, "code": code}

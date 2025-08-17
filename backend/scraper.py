import sys
import tempfile
import subprocess
import json
import requests
from pydantic import BaseModel
import os
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise RuntimeError("Define la variable de entorno OPENROUTER_API_KEY en .env")


class ScrapeRequest(BaseModel):
    url: str
    instruction: str

def clean_code(code: str) -> str:
    # Elimina bloques markdown ```python ... ```
    if code.startswith("```") and code.endswith("```"):
        code = code.strip("`").strip()
        if code.startswith("python"):
            code = code[len("python"):].strip()
    return code

def generate_scraper_code(url: str, instruction: str) -> str:
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    prompt = [
        {
            "role": "system",
            "content": (
                "Eres un experto en Python para scraping web. "
                "Genera únicamente código Python válido, sin explicaciones ni markdown. "
                "Usa solo requests y BeautifulSoup. "
                "El código debe imprimir un JSON válido."
            )
        },
        {
            "role": "user",
            "content": f"Genera código para scrapear {url} siguiendo esta instrucción: {instruction}"
        }
    ]

    payload = {
        "model": "openai/gpt-4o-mini",
        "messages": prompt,
        "temperature": 0,
        "max_tokens": 512,
    }

    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
    if response.status_code != 200:
        raise RuntimeError(f"OpenRouter API error: {response.status_code} {response.text}")

    result = response.json()
    code_raw = result["choices"][0]["message"]["content"]
    return clean_code(code_raw)

def run_scraper(request: ScrapeRequest):
    code = generate_scraper_code(request.url, request.instruction)

    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as tmp:
        tmp.write(code)
        tmp.flush()

        proc = subprocess.run(
            [sys.executable, tmp.name],
            capture_output=True,
            text=True,
            timeout=30
        )

    if proc.returncode != 0:
        raise RuntimeError(f"Error ejecutando scraper: {proc.stderr}")

    data = json.loads(proc.stdout)
    return {"data": data, "code": code}


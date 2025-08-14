import os
import subprocess
import tempfile
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import requests
from dotenv import load_dotenv
import sys

load_dotenv()  # carga variables del .env

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise RuntimeError("Define la variable de entorno OPENROUTER_API_KEY con tu API key")

# Define los modelos Pydantic antes de usarlos
class ScrapeRequest(BaseModel):
    url: str
    instruction: str

class ScrapeResponse(BaseModel):
    data: list
    code: str

def clean_code(code: str) -> str:
    # Elimina bloques markdown ```python ... ```
    if code.startswith("```") and code.endswith("```"):
        code = code.strip("`")
        code = code.strip()
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
                "Genera únicamente código Python que funcione para hacer scraping. "
                "No escribas explicaciones, comentarios ni markdown. "
                "Usa solo requests y BeautifulSoup. "
                "El código debe imprimir un JSON válido con los datos extraídos."
            )
        },
        {
            "role": "user",
            "content": (
                f"Genera código Python para scrapear la web {url} siguiendo esta instrucción: {instruction}. "
                "Solo código, sin texto extra."
            )
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
@app.get("/")
def health():
    return {"status": "ok"}
@app.options("/")
async def root_options():
    return {}

@app.post("/", response_model=ScrapeResponse)
def scrape(request: ScrapeRequest):
    try:
        code = generate_scraper_code(request.url, request.instruction)
        print("CODIGO DEVUELTO POR EL MODELO:")
        print(code)  # Para debug: ver qué devuelve el modelo
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as tmp:
            tmp.write(code)
            tmp.flush()

            proc = subprocess.run(
                [sys.executable, tmp.name],
                capture_output=True,
                text=True,
                timeout=30,
                encoding="utf-8"
            )

        if proc.returncode != 0:
            raise HTTPException(status_code=500, detail=f"Error ejecutando código de scraping: {proc.stderr}")

        data = json.loads(proc.stdout)
        return {"data": data, "code": code}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

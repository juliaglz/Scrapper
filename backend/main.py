import os
import uvicorn
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import scraper
import stt
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Healthcheck
@app.get("/")
def health():
    return {"status": "ok"}

# Scraping endpoint
@app.post("/scrape")
def scrape(request: scraper.ScrapeRequest):
    try:
        return scraper.run_scraper(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Speech-to-text endpoint
@app.post("/stt")
async def speech_to_text(file: UploadFile = File(...)):
    try:
        return await stt.speech_to_text(file)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

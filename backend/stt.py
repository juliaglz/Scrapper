import os
import requests
from fastapi import UploadFile
from dotenv import load_dotenv

load_dotenv()
ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY")
STT_MODEL = "scribe_v1"

async def speech_to_text(file: UploadFile):
    # Leer el archivo .weba directamente
    audio_bytes = await file.read()

    files = {"file": (file.filename, audio_bytes, "audio/webm")}
    data = {"model_id": STT_MODEL}  # campo correcto en la API
    headers = {"xi-api-key": ELEVEN_API_KEY}

    response = requests.post(
        "https://api.elevenlabs.io/v1/speech-to-text",
        headers=headers,
        files=files,
        data=data
    )

    if response.status_code != 200:
        raise RuntimeError(f"11Labs STT error: {response.text}")

    return response.json()

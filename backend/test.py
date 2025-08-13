import requests

response = requests.post(
    "http://127.0.0.1:8000/scrape",
    json={
        "url": "https://quotes.toscrape.com/",
        "instruction": "Extrae las citas y autores."
    }
)

print(response.json())

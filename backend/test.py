from scraper import ScrapeRequest, fetch_page_simple, fetch_page_playwright, run_scraper

# Example request
req = ScrapeRequest(
    url="https://www.mk2palaciodehielo.es/es/cartelera",
    instruction="Extract movie titles from the page"
)

# --- Print simple requests structure ---
try:
    simple_structure = fetch_page_simple(req.url)
    print("=== Simple Structure ===")
    print(simple_structure[:2000])  # print first 2000 chars for readability
except Exception as e:
    print(f"Simple method failed: {e}")

# --- Print Playwright structure ---
try:
    playwright_structure = fetch_page_playwright(req.url)
    print("\n=== Playwright Structure ===")
    print(playwright_structure[:2000])  # first 2000 chars
except Exception as e:
    print(f"Playwright method failed: {e}")

# --- Run the scraper normally ---
result = run_scraper(req)
print("\n=== DATA ===")
print(result["data"])
print("\n=== CODE GENERATED ===")
print(result["code"])

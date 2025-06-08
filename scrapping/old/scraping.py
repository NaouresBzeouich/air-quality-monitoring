import requests
import json
import time

API_KEY = "ad820b2a38ba877cdf3150e897e6a00ee58074dc60f9f582bb7d5c475b4f0d78"  # 🔑 Replace with your actual OpenAQ API key
BASE_URL = "https://api.openaq.org/v3/locations"
LIMIT = 1000
output = []

HEADERS = {
    "x-api-key": API_KEY
}

def fetch_all_locations():
    page = 13

    while True:
        params = {
            "limit": LIMIT,
            "page": page,
            "order_by": "id",
            "sort_order": "asc"
        }

        response = requests.get(BASE_URL, params=params, headers=HEADERS)
        if response.status_code != 200:
            print(f"Error on page {page}: {response.status_code}")
            break

        data = response.json()
        results = data.get("results", [])

        if not results:
            print(f"No more data at page {page}. Stopping.")
            break

        print(f"Fetched page {page} - {len(results)} locations")
        output.extend(results)
        page += 1
        time.sleep(0.2)

    return output

# Run and save
all_locations = fetch_all_locations()

with open("openaq_locations_2.json", "w", encoding="utf-8") as f:
    json.dump(all_locations, f, indent=2, ensure_ascii=False)

print(f"\n✅ Done! {len(all_locations)} locations saved to 'openaq_locations.json'")

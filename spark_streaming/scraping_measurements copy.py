import requests
import json
import time
import os

API_KEY = "ad820b2a38ba877cdf3150e897e6a00ee58074dc60f9f582bb7d5c475b4f0d78"
HEADERS = {"x-api-key": API_KEY}
LIMIT = 1000
MAX_LIMIT = 40
BASE_URL = "https://api.openaq.org/v3/sensors"
PROGRESS_FILE = "sensors_data/over_all_progress.json"

os.makedirs("sensors_data", exist_ok=True)

session = requests.Session()

def load_locations(path="openaq_locations.json"):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def initialize_progress(locations):
    progress = {}
    for loc in locations:
        for sensor in loc.get("sensors", []):
            sensor_id = str(sensor.get("id"))
            if sensor_id:
                progress[sensor_id] = {
                    "last_page_fetched": 0,
                    "is_done": False
                }
    return progress


def load_progress(locations):
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    progress = initialize_progress(locations)
    save_progress(progress)
    return progress


def save_progress(progress):
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(progress, f, indent=2)


def request_with_retries(url, params, retries=5, delay=0.5):
    for attempt in range(retries):
        try:
            response = session.get(url, headers=HEADERS, params=params)


            if response.status_code == 200:
                return response
            print(f"⚠️ Attempt {attempt + 1} failed with status {response.status_code}")
        except Exception as e:
            print(f"⚠️ Attempt {attempt + 1} raised error: {e}")
        time.sleep(delay)
    return None


def fetch_measurements(sensor_id, progress):
    current_progress = progress[sensor_id]
    if current_progress["is_done"]:
        print(f"⏭️ Skipping sensor {sensor_id} (already marked done)")
        return

    page = current_progress["last_page_fetched"] + 1
    chunk = []
    chunk_start = page

    while True:
        url = f"{BASE_URL}/{sensor_id}/measurements"
        params = {
            "limit": LIMIT,
            "page": page,
            "sort": "desc"
        }

        response = request_with_retries(url, params)
        if not response:
            print(f"❌ Sensor {sensor_id} - Failed after retries on page {page}")
            progress[sensor_id]["last_page_fetched"] = page - 1
            save_progress(progress)
            break

        data = response.json()
        results = data.get("results", [])
        if not results:
            print(f"✅ Sensor {sensor_id} - No more data at page {page}")
            progress[sensor_id]["last_page_fetched"] = page - 1
            progress[sensor_id]["is_done"] = True
            save_progress(progress)
            break

        print(f"📦 Sensor {sensor_id} → Page {page} → {len(results)} measurements")
        chunk.extend(results)

        if (page - chunk_start + 1) % 10 == 0:
            file_path = f"sensors_data/sensor_{sensor_id}_{chunk_start}_{page}.json"
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump({
                    "sensorId": sensor_id,
                    "startPage": chunk_start,
                    "endPage": page,
                    "measurements": chunk
                }, f, indent=2, ensure_ascii=False)

            progress[sensor_id]["last_page_fetched"] = page
            save_progress(progress)
            chunk = []
            chunk_start = page + 1

        if page >= MAX_LIMIT:
            print(f"❎ Sensor {sensor_id} - Hit page limit ( {MAX_LIMIT})")
            progress[sensor_id]["last_page_fetched"] = page
            progress[sensor_id]["is_done"] = True
            save_progress(progress)
            break

        page += 1

    # Save remaining data if any
    if chunk:
        file_path = f"sensors_data/sensor_{sensor_id}_{chunk_start}_{page - 1}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump({
                "sensorId": sensor_id,
                "startPage": chunk_start,
                "endPage": page - 1,
                "measurements": chunk
            }, f, indent=2, ensure_ascii=False)

        progress[sensor_id]["last_page_fetched"] = page - 1
        save_progress(progress)


def scrape_all_sensors(locations):
    progress = load_progress(locations)
    seen_sensors = set(progress.keys())

    for sensor_id in seen_sensors:
        print(f"\n🚀 Starting sensor {sensor_id} from page {progress[sensor_id]['last_page_fetched'] + 1}")
        fetch_measurements(sensor_id, progress)

    print(f"\n🎉 Done! Scraped and saved measurements for {len(seen_sensors)} sensors.")


# Run everything
locations = load_locations()
scrape_all_sensors(locations)

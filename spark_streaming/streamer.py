import requests
import json
import time
import os
import csv
from datetime import datetime, timedelta
import threading
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("openaq_fetcher.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger()

# Configuration
API_KEY = "ad820b2a38ba877cdf3150e897e6a00ee58074dc60f9f582bb7d5c475b4f0d78"
HEADERS = {"x-api-key": API_KEY}
LIMIT = 1000
BASE_URL = "https://api.openaq.org/v3/sensors"
PROGRESS_FILE = "data/progress.json"
SENSORS_FILE = "sensors.json"
DATA_DIR = "data"
CSV_DIR = "csv_data"

# Create necessary directories
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(CSV_DIR, exist_ok=True)

# Rate limiting
class RateLimiter:
    def __init__(self, requests_per_minute=60, requests_per_hour=2000):
        self.minute_limit = requests_per_minute
        self.hour_limit = requests_per_hour
        self.minute_requests = []
        self.hour_requests = []
        self.lock = threading.Lock()
    
    def wait_if_needed(self):
        now = time.time()
        with self.lock:
            # Clean up old timestamps
            self.minute_requests = [t for t in self.minute_requests if now - t < 60]
            self.hour_requests = [t for t in self.hour_requests if now - t < 3600]
            
            # Check if we need to wait
            if len(self.minute_requests) >= self.minute_limit:
                sleep_time = 60 - (now - self.minute_requests[0])
                if sleep_time > 0:
                    logger.info(f"Rate limit: Waiting {sleep_time:.2f}s for minute limit")
                    time.sleep(sleep_time)
            
            if len(self.hour_requests) >= self.hour_limit:
                sleep_time = 3600 - (now - self.hour_requests[0])
                if sleep_time > 0:
                    logger.info(f"Rate limit: Waiting {sleep_time:.2f}s for hour limit")
                    time.sleep(sleep_time)
            
            # Record this request
            current_time = time.time()
            self.minute_requests.append(current_time)
            self.hour_requests.append(current_time)

rate_limiter = RateLimiter()

def load_sensors():
    """Load sensor IDs from the sensors.json file"""
    try:
        with open(SENSORS_FILE, "r", encoding="utf-8") as f:
            return [x["id"] for x in json.load(f)]
    except FileNotFoundError:
        logger.error(f"Sensors file {SENSORS_FILE} not found")
        return []

def load_progress():
    """Load progress data or create a new progress file if it doesn't exist"""
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    
    # Create new progress file with initialized values
    sensors = load_sensors()
    progress = {}
    
    for sensor_id in sensors:
        progress[str(sensor_id)] = {
            "lastFetched": 0,  # 0 means never fetched
            "totalRegistries": 0
        }
    
    save_progress(progress)
    return progress

def save_progress(progress):
    """Save progress data to file"""
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(progress, f, indent=2)

def request_with_retries(url, params, retries=5, delay=1):
    """Make API request with retries and rate limiting"""
    rate_limiter.wait_if_needed()
    
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=HEADERS, params=params)
            if response.status_code == 200:
                return response
            elif response.status_code == 429:  # Too Many Requests
                wait_time = 60 if attempt == 0 else 60 * (2 ** attempt)
                logger.warning(f"Rate limit hit. Waiting {wait_time}s before retry.")
                time.sleep(wait_time)
            else:
                logger.warning(f"Attempt {attempt + 1} failed with status {response.status_code}")
                time.sleep(delay * (2 ** attempt))  # Exponential backoff
        except Exception as e:
            logger.error(f"Attempt {attempt + 1} raised error: {e}")
            time.sleep(delay * (2 ** attempt))
    
    logger.error(f"All retries failed for URL: {url}")
    return None

def save_to_csv(sensor_id, measurements, date_from, date_to):
    """Save measurements to CSV file"""
    if not measurements:
        return
    
    # Format the dates for the filename
    from_str = date_from.strftime('%Y%m%d')
    to_str = date_to.strftime('%Y%m%d')
    
    # Create the filename
    filename = f"{CSV_DIR}/sensor_{sensor_id}-{from_str}-{to_str}.csv"
    print("measurements")
    print(measurements)
    print("measurements.len")
    print(len(measurements))
    # Extract headers from the first result
    if measurements and len(measurements) > 0:
        # Flatten the nested structure for CSV
        flattened_data = []
        for m in measurements:
            print("m")
            print(m)
            row = {
                    "value": m["value"] if "value" in m else None,
                    "has_flags": m["flagInfo"]["hasFlags"] if "flagInfo" in m and "hasFlags" in m["flagInfo"] else False,
                    "parameter_id": m["parameter"]["id"] if "parameter" in m and "id" in m["parameter"] else None,
                    "parameter_name": m["parameter"]["name"] if "parameter" in m and "name" in m["parameter"] else None,
                    "parameter_units": m["parameter"]["units"] if "parameter" in m and "units" in m["parameter"] else None,
                    "parameter_display_name": m["parameter"]["displayName"] if "parameter" in m and "displayName" in m["parameter"] else None,
                    "period_label": m["period"]["label"] if "period" in m and "label" in m["period"] else None,
                    "period_interval": m["period"]["interval"] if "period" in m and "interval" in m["period"] else None,
                    "datetime_from_utc": m["period"]["datetimeFrom"]["utc"] if "period" in m and "datetimeFrom" in m["period"] and "utc" in m["period"]["datetimeFrom"] else None,
                    "datetime_from_local": m["period"]["datetimeFrom"]["local"] if "period" in m and "datetimeFrom" in m["period"] and "local" in m["period"]["datetimeFrom"] else None,
                    "datetime_to_utc": m["period"]["datetimeTo"]["utc"] if "period" in m and "datetimeTo" in m["period"] and "utc" in m["period"]["datetimeTo"] else None,
                    "datetime_to_local": m["period"]["datetimeTo"]["local"] if "period" in m and "datetimeTo" in m["period"] and "local" in m["period"]["datetimeTo"] else None,
                    "latitude": m["coordinates"]["latitude"] if "coordinates" in m and "latitude" in m["coordinates"] else None,
                    "longitude": m["coordinates"]["longitude"] if "coordinates" in m and "longitude" in m["coordinates"] else None
                }
            print("row")
            print(row)
            flattened_data.append(row)
        
        # Write to CSV
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            if flattened_data:
                fieldnames = flattened_data[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(flattened_data)
                logger.info(f"Saved {len(flattened_data)} records to {filename}")
    else:
        logger.warning(f"No data to write for sensor {sensor_id}")

def fetch_measurements_for_sensor(sensor_id, progress_data):
    """Fetch measurements for a specific sensor"""
    # Determine date range based on last fetch time
    now = datetime.utcnow()
    
    if progress_data["lastFetched"] == 0:
        # First time fetching - get the last 30 days of data
        date_from = now - timedelta(days=30)
    else:
        # Get data since last fetch
        date_from = datetime.fromtimestamp(progress_data["lastFetched"])
    
    date_to = now
    
    # Format dates for API
    date_from_str = date_from.strftime('%Y-%m-%dT%H:%M:%SZ')
    date_to_str = date_to.strftime('%Y-%m-%dT%H:%M:%SZ')
    
    logger.info(f"Fetching sensor {sensor_id} data from {date_from_str} to {date_to_str}")
    
    # Prepare API request
    url = f"{BASE_URL}/{sensor_id}/measurements"
    params = {
        # "limit": LIMIT,
        # "datetime_from": date_from_str,
        # "datetime_to": date_to_str
    }
    
    # Make the request
    response = request_with_retries(url, params)
    if not response:
        logger.error(f"Failed to fetch data for sensor {sensor_id}")
        return
    
    
    data = response.json()
    
    
    print("data")
    
    
    # Process response
    results = data["results"]    
    # Update progress
    if results:
        progress_data["totalRegistries"] += len(results)
        progress_data["lastFetched"] = int(time.time())
        
        # Save to CSV
        save_to_csv(sensor_id, results, date_from, date_to)
        
        logger.info(f"Fetched {len(results)} measurements for sensor {sensor_id}")
    else:
        logger.info(f"No new data for sensor {sensor_id}")
        # Still update last fetched time
        progress_data["lastFetched"] = int(time.time())
    
    return len(results) > 0

def main_loop():
    """Main function that runs every 60 seconds"""
    while True:
        try:
            # Load progress data
            progress = load_progress()
            
            # Load sensor IDs
            sensors = load_sensors()
            
            # Process each sensor
            for sensor_id in sensors:
                sensor_id = str(sensor_id)
                if sensor_id not in progress:
                    progress[sensor_id] = {
                        "lastFetched": 0,
                        "totalRegistries": 0
                    }
                
                # Fetch data for this sensor
                fetch_measurements_for_sensor(sensor_id, progress[sensor_id])
                
                # Save progress after each sensor to prevent data loss
                save_progress(progress)
            
            logger.info(f"Completed fetch cycle. Waiting 60 seconds.")
            time.sleep(60)  # Wait for 60 seconds before next cycle
            
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
            time.sleep(60)  # Still wait before retrying

if __name__ == "__main__":
    logger.info("Starting OpenAQ Sensor Data Fetcher")
    main_loop()
# from confluent_kafka import Producer
from confluent_kafka import Producer
import requests
import json
import time
from datetime import datetime, timedelta
import csv
import os
from pathlib import Path

API_KEY = "ad820b2a38ba877cdf3150e897e6a00ee58074dc60f9f582bb7d5c475b4f0d78"
MEASUREMENTS_BASE_URL = "https://api.openaq.org/v3/sensors/{}/measurements"
KAFKA_BROKER = "localhost:9092"
KAFKA_TOPIC = "openaq-measurements"

HEADERS = {
    "x-api-key": API_KEY
}

# Rate limiting constants
MINUTE_LIMIT = 60
HOUR_LIMIT = 2000
MINUTE_RESET_TIME = 60  # seconds
HOUR_RESET_TIME = 3600  # seconds

# CSV constants
CSV_HEADERS = ['location_id', 'sensor_id', 'location', 'datetime', 'lat', 'lon', 'parameter', 'unit', 'value']
CSV_DIR = "measurements_data"

# Initialize Kafka producer
producer = Producer({
    'bootstrap.servers': KAFKA_BROKER,
    'client.id': 'openaq-producer'
})

def delivery_report(err, msg):
    """Callback for Kafka message delivery"""
    if err is not None:
        print(f"❌ Message delivery failed: {err}")
    else:
        print(f"✅ Message delivered to {msg.topic()} [{msg.partition()}]")

class RateLimiter:
    def __init__(self):
        self.minute_requests = 0
        self.hour_requests = 0
        self.last_minute_reset = datetime.now()
        self.last_hour_reset = datetime.now()

    def check_and_wait(self):
        now = datetime.now()
        
        # Reset minute counter if a minute has passed
        if (now - self.last_minute_reset).total_seconds() >= MINUTE_RESET_TIME:
            self.minute_requests = 0
            self.last_minute_reset = now

        # Reset hour counter if an hour has passed
        if (now - self.last_hour_reset).total_seconds() >= HOUR_RESET_TIME:
            self.hour_requests = 0
            self.last_hour_reset = now

        # Check minute limit
        if self.minute_requests >= MINUTE_LIMIT:
            wait_time = MINUTE_RESET_TIME - (now - self.last_minute_reset).total_seconds()
            if wait_time > 0:
                print(f"⏳ Reached minute limit. Waiting for {wait_time:.1f} seconds...")
                time.sleep(wait_time)
                self.minute_requests = 0
                self.last_minute_reset = datetime.now()

        # Check hour limit
        if self.hour_requests >= HOUR_LIMIT:
            wait_time = HOUR_RESET_TIME - (now - self.last_hour_reset).total_seconds()
            if wait_time > 0:
                print(f"⏳ Reached hourly limit. Waiting for {wait_time/60:.1f} minutes...")
                time.sleep(wait_time)
                self.hour_requests = 0
                self.last_hour_reset = datetime.now()

        self.minute_requests += 1
        self.hour_requests += 1

def ensure_csv_dir():
    """Ensure the CSV directory exists"""
    Path(CSV_DIR).mkdir(parents=True, exist_ok=True)

def get_csv_path(location_id):
    """Get the path for a location's CSV file"""
    return os.path.join(CSV_DIR, f"{location_id}.csv")

def save_measurements_to_csv(location_id, location_name, lat, lon, sensor_id, measurements):
    """Save measurements to a CSV file and send to Kafka, with newest data on top"""
    csv_path = get_csv_path(location_id)
    
    # Read existing data if file exists
    existing_data = []
    if os.path.exists(csv_path):
        with open(csv_path, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            existing_data = list(reader)

    # Prepare new measurements
    new_data = []
    for m in measurements:
        # Extract nested values
        parameter = m.get('parameter', {})
        period = m.get('period', {})
        datetime_from = period.get('datetimeFrom', {}).get('utc')

        new_row = {
            'location_id': location_id,
            'sensor_id': sensor_id,
            'location': location_name,
            'datetime': datetime_from,
            'lat': lat,
            'lon': lon,
            'parameter': parameter.get('name'),
            'unit': parameter.get('units'),
            'value': m.get('value')
        }
        new_data.append(new_row)
        
        # Create CSV string for Kafka
        csv_string = ','.join(str(new_row[field]) for field in CSV_HEADERS)
        
        # Send to Kafka
        try:
            producer.produce(
                KAFKA_TOPIC,
                key=str(location_id),  # Use location_id as the key for partitioning
                value=csv_string,
                callback=delivery_report
            )
            # Trigger any available delivery report callbacks
            producer.poll(0)
        except Exception as e:
            print(f"❌ Failed to send to Kafka: {e}")

    # Combine new and existing data
    all_data = new_data + existing_data

    # Write all data back to file
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
        writer.writeheader()
        writer.writerows(all_data)

    # Make sure all messages are sent
    producer.flush()

# Load locations file
with open("openaq_locations.json", "r", encoding="utf-8") as f:
    locations = json.load(f)

rate_limiter = RateLimiter()
ensure_csv_dir()

total_measurements = 0

for loc in locations:
    location_id = loc.get('id')
    location_name = loc.get('name')
    coordinates = loc.get('coordinates', {})
    lat = coordinates.get('latitude')
    lon = coordinates.get('longitude')
    
    sensors = loc.get("sensors", [])
    for sensor in sensors:
        sensor_id = sensor.get("id")
        if sensor_id is None:
            continue

        url = MEASUREMENTS_BASE_URL.format(sensor_id)
        # Get current time and 3 days ago in ISO format with UTC timezone
        current_time = datetime.utcnow()
        three_days_ago = current_time - timedelta(days=3)
        
        current_time_str = current_time.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
        three_days_ago_str = three_days_ago.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
        
        params = {
            "limit": 1000,
            "datetime_from": three_days_ago_str,
            "datetime_to": current_time_str
        }

        try:
            # Check rate limits before making request
            rate_limiter.check_and_wait()
            
            response = requests.get(url, headers=HEADERS, params=params)
            if response.status_code != 200:
                print(f"⚠️ Sensor {sensor_id}: HTTP {response.status_code}")
                continue

            data = response.json()
            measurements = data.get("results", [])

            if measurements:
                print(f"📦 Sensor {sensor_id} - {len(measurements)} measurements")
                save_measurements_to_csv(location_id, location_name, lat, lon, sensor_id, measurements)
                total_measurements += len(measurements)

            time.sleep(0.2)  # Small delay between requests

        except Exception as e:
            print(f"❌ Exception on sensor {sensor_id}: {e}")
            continue

print(f"\n✅ Done! {total_measurements} total measurements saved to CSV files in '{CSV_DIR}' directory")

try:
    # Your existing code here
    pass
finally:
    # Make sure to flush any remaining messages before exiting
    producer.flush()
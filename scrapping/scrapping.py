# from confluent_kafka import Producer
import requests
import json
import time

API_KEY = "ad820b2a38ba877cdf3150e897e6a00ee58074dc60f9f582bb7d5c475b4f0d78"
BASE_URL = "https://api.openaq.org/v3/locations"
LIMIT = 1000

KAFKA_BROKER = "localhost:9092"  # Change to your broker address
KAFKA_TOPIC = "openaq-locations" # Change to your topic name

HEADERS = {
    "x-api-key": API_KEY
}

# producer = Producer({'bootstrap.servers': KAFKA_BROKER})

def delivery_report(err, msg):
    if err is not None:
        print(f"❌ Delivery failed: {err}")
    else:
        print(f"✅ Message delivered to {msg.topic()} [{msg.partition()}]")

def fetch_all_locations():
    page = 1
    all_locations = []

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
        all_locations.extend(results)

        # Send each location as a separate Kafka message
        # for location in results:
        #     producer.produce(
        #         KAFKA_TOPIC,
        #         value=json.dumps(location, ensure_ascii=False),
        #         callback=delivery_report
        #     )
        # producer.flush()  # Ensure delivery before next page

        page += 1
        time.sleep(0.2)

    return all_locations

# Run and save
all_locations = fetch_all_locations()

with open("openaq_locations.json", "w", encoding="utf-8") as f:
    json.dump(all_locations, f, indent=2, ensure_ascii=False)

print(f"\n✅ Done! {len(all_locations)} locations saved to 'openaq_locations.json'")
from confluent_kafka import Consumer, KafkaException
import sys

KAFKA_BROKER = 'localhost:9092'
KAFKA_TOPIC = 'openaq-locations'
KAFKA_GROUP = 'openaq-consumer-group'

conf = {
    'bootstrap.servers': KAFKA_BROKER,
    'group.id': KAFKA_GROUP,
    'auto.offset.reset': 'earliest',
}

consumer = Consumer(conf)
consumer.subscribe([KAFKA_TOPIC])

print(f"Subscribed to topic '{KAFKA_TOPIC}'. Waiting for messages...")

try:
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            print(f"Consumer error: {msg.error()}")
            continue
        print(f"Received message: {msg.value().decode('utf-8')}")
except KeyboardInterrupt:
    print("\nExiting...")
finally:
    consumer.close() 
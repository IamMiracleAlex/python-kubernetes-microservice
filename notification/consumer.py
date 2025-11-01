import json, os
# from email import notification_mail
from confluent_kafka import Consumer


KAFKA_BOOTSTRAP_SERVERS = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")

consumer_config = {
    "bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS,
    "group.id": "notification",
    "auto.offset.reset": "earliest"
}

consumer = Consumer(consumer_config)
consumer.subscribe(["mp3"])


def main():
    print("🟢 Notification service is running and waiting for messages. To exit press CTRL+C")

    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue

        if msg.error():
            print("❌ Consumer error:\n", msg.error())
            continue
        
        print("📩 Message received")

        try:
            value = msg.value().decode("utf-8")
            message = json.loads(value)
            # notification_mail(message)
            print(f"📦 User: {message['username']} notified")
        except Exception as err:
            print("Error ouccrred while processing video")
            print(err)

    

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🔴 Stopping notification service")

    finally:
        consumer.close()

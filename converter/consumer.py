import os, json
from pymongo import MongoClient
import gridfs
from to_mp3 import convert
from confluent_kafka import Consumer, Producer


KAFKA_BOOTSTRAP_SERVERS = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")

MONGO_HOST = os.environ.get("MONGO_HOST", "localhost")

producer_config = {
    "bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS,
}
consumer_config = {
    "bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS,
    "group.id": "video-tracker",
    "auto.offset.reset": "earliest"
}

producer = Producer(producer_config)
consumer = Consumer(consumer_config)
consumer.subscribe(["video"])


def main():
    client = MongoClient(MONGO_HOST, 27017)
    db_videos = client.videos
    db_mp3s = client.mp3s

    # gridfs
    fs_videos = gridfs.GridFS(db_videos)
    fs_mp3s = gridfs.GridFS(db_mp3s)

    print("🟢 Converter service is running and waiting for messages. To exit press CTRL+C")

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
            convert(message, fs_videos, fs_mp3s, producer)
            print(f"📦 Messeged processed: {message['video_fid']} - from {message['username']}")
        except Exception as err:
            print("Error ouccrred while processing video")
            print(err)

    

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🔴 Stopping converter service")

    finally:
        consumer.close()

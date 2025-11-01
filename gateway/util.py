import json, os
from bson.objectid import ObjectId


VIDEO_TOPIC = os.environ.get("VIDEO_TOPIC", "video")


class DeliveryReport:
    def __init__(self, fs):
        self.fs = fs

    def __call__(self, err, msg):
        message = json.loads(msg.value().decode("utf-8"))
        if err:
            self.fs.delete(ObjectId(message["video_fid"]))
            print(f"❌ Delivery failed: {err}")
        else:
            print(f"✅ Delivered {msg.value().decode('utf-8')}")
            print(f"✅ Delivered to {msg.topic()} : partition {msg.partition()} : at offset {msg.offset()}")


def upload(file, fs, producer, access):
    try:
        fid = fs.put(file)
    except Exception as err:
        print(err)
        return "internal server error", 500

    message = {
        "video_fid": str(fid),
        "mp3_fid": None,
        "username": access["username"],
    }

    value = json.dumps(message).encode("utf-8")

    delivery_report = DeliveryReport(fs)
    producer.produce(
        topic=VIDEO_TOPIC,
        value=value,
        callback=delivery_report
    )

    producer.flush()

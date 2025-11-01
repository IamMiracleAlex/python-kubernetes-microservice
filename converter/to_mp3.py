import tempfile, os, json
from bson.objectid import ObjectId
import moviepy.editor

MP3_TOPIC = os.environ.get("VIDEO_TOPIC", "mp3")


class DeliveryReport:
    def __init__(self, fs):
        self.fs = fs

    def __call__(self, err, msg):
        message = json.loads(msg.value().decode("utf-8"))
        if err:
            self.fs.delete(ObjectId(message["mp3_fid"]))
            print(f"❌ Delivery failed: {err}")
        else:
            print(f"✅ Delivered {msg.value().decode('utf-8')}")
            print(f"✅ Delivered to {msg.topic()} : partition {msg.partition()} : at offset {msg.offset()}")


def convert(message, fs_videos, fs_mp3s, producer):

    # empty temp file
    tf = tempfile.NamedTemporaryFile()
    # video contents
    out = fs_videos.get(ObjectId(message["video_fid"]))
    # add video contents to empty file
    tf.write(out.read())
    # create audio from temp video file
    audio = moviepy.editor.VideoFileClip(tf.name).audio
    tf.close()

    # write audio to the file
    tf_path = tempfile.gettempdir() + f"/{message['video_fid']}.mp3"
    audio.write_audiofile(tf_path)

    # save file to mongo
    f = open(tf_path, "rb")
    data = f.read()
    fid = fs_mp3s.put(data)
    f.close()
    os.remove(tf_path)

    message["mp3_fid"] = str(fid)


    value = json.dumps(message).encode("utf-8")

    delivery_report = DeliveryReport(fs_mp3s)
    producer.produce(
        topic=MP3_TOPIC,
        value=value,
        callback=delivery_report
    )
    producer.flush()


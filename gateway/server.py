import os, gridfs, json
from flask import Flask, request, send_file
from pymongo import MongoClient
from validate import token
from access import login, register
from util import upload
from bson.objectid import ObjectId
from confluent_kafka import Producer


server = Flask(__name__)

# KAFKA_HOST = os.environ.get("KAFKA_HOST") # "localhost"
# KAFKA_PORT = os.environ.get("KAFKA_PORT")  # "9092"
# KAFKA_BOOTSTRAP_SERVERS = f"{KAFKA_HOST}:{KAFKA_PORT}"
KAFKA_BOOTSTRAP_SERVERS = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
MONGO_HOST = os.environ.get("MONGO_HOST", "localhost") #"host.docker.internal"

client = MongoClient(MONGO_HOST, 27017)
mongo_video = client.videos
mongo_mp3 = client.mp3s


fs_videos = gridfs.GridFS(mongo_video)
fs_mp3s = gridfs.GridFS(mongo_mp3)

producer_config = {
    "bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS,
}

producer = Producer(producer_config)


@server.route("/login", methods=["POST"])
def gateway_login():
    token, err = login(request)

    if not err:
        return token
    else:
        return err


@server.route("/upload", methods=["POST"])
def gateway_upload():
    access, err = token(request)

    if err:
        return err

    access = json.loads(access)
    # print(access, "access")

    if access["admin"]:
        if len(request.files) > 1 or len(request.files) < 1:
            return "exactly 1 file required", 400

        for _, f in request.files.items():
            err = upload(f, fs_videos, producer, access)

            if err:
                return err

        return "success!", 200
    else:
        return "not authorized", 401


@server.route("/download", methods=["GET"])
def download():
    access, err = token(request)

    if err:
        return err

    access = json.loads(access)

    if access["admin"]:
        fid_string = request.args.get("fid")

        if not fid_string:
            return "fid is required", 400

        try:
            out = fs_mp3s.get(ObjectId(fid_string))
            return send_file(out, download_name=f"{fid_string}.mp3")
        except Exception as err:
            raise err
            # print(err)
            # return "internal server error", 500

    return "not authorized", 401


@server.route("/register", methods=["POST"])
def gateway_register():
    result, err = register(request)

    if err:
        return err

    return result, 201


@server.route("/")
def home():
    return "API Gateway!"



if __name__ == "__main__":
    server.run(host="0.0.0.0", port=8000, debug=True)

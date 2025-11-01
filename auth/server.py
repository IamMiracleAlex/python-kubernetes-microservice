import jwt, datetime, os
from flask import Flask, request
import psycopg2

server = Flask(__name__)

POSTGRES_HOST = os.environ.get("POSTGRES_HOST", "localhost") #"host.docker.internal
POSTGRES_USER = os.environ.get("POSTGRES_USER", "authuser")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "password123")
POSTGRES_DB = os.environ.get("POSTGRES_DB", "authdb")
POSTGRES_PORT = int(os.environ.get("POSTGRES_PORT", 5432))
JWT_SECRET = os.environ.get("JWT_SECRET", "sample_secret_key")

# helper to get a new Postgres connection
def get_db_connection():
    return psycopg2.connect(
        host=POSTGRES_HOST,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        dbname=POSTGRES_DB,
        port=int(POSTGRES_PORT),
    )


@server.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    user_email = data.get("email")
    user_password = data.get("password")

    if not user_email or not user_password:
        return "missing credentials", 401

    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            'SELECT email, password FROM "users" WHERE email = %s', (user_email,)
        )
        user_row = cur.fetchone()

        if user_row:
            email, password = user_row[0], user_row[1]

            if user_email != email or user_password != password:
                return "invalid credentials", 401
            else:
                return createJWT(user_email, JWT_SECRET, True)
        else:
            return "invalid credentials", 401
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


@server.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    if not data or not data.get("email") or not data.get("password"):
        return "missing email or password", 400

    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            'INSERT INTO "users" (email, password) VALUES (%s, %s) RETURNING id',
            (data["email"], data["password"]),
        )
        user_id = cur.fetchone()[0]
        conn.commit()
        return {"id": user_id, "email": data["email"]}, 201
    except psycopg2.IntegrityError:
        if conn:
            conn.rollback()
        return "user already exists", 409
    except Exception as e:
        if conn:
            conn.rollback()
        print(e)
        return "internal server error", 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


@server.route("/validate", methods=["POST"])
def validate():
    encoded_jwt = request.headers.get("Authorization")
    if not encoded_jwt:
        return "missing credentials", 401

    parts = encoded_jwt.split(" ")
    if len(parts) != 2:
        return "invalid authorization header", 401

    token = parts[1]

    try:
        decoded = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    except Exception:
        return "not authorized", 403

    return decoded, 200


def createJWT(username, secret, authz):
    return jwt.encode(
        {
            "username": username,
            "exp": datetime.datetime.now(tz=datetime.timezone.utc)
            + datetime.timedelta(days=1),
            "iat": datetime.datetime.now(tz=datetime.timezone.utc),
            "admin": authz,
        },
        secret,
        algorithm="HS256",
    )


@server.route("/")
def home():
    return "Auth Service!"



if __name__ == "__main__":
    server.run(host="0.0.0.0", port=5050, debug=True)

import os, requests


AUTH_SVC_ADDRESS = os.environ.get("AUTH_SVC_ADDRESS", "auth:5050")

def login(request):
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        return None, ("missing credentials", 401)

    data = {"email": email, "password": password}

    response = requests.post(
        f"http://{AUTH_SVC_ADDRESS}/login", data=data
    )

    if response.status_code == 200:
        return response.text, None
    else:
        return None, (response.text, response.status_code)


def register(request):
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        return None, ("missing email or password", 400)

    data = {"email": email, "password": password}

    response = requests.post(
        f"http://{AUTH_SVC_ADDRESS}/register", json=data
    )

    if response.status_code == 201:
        return response.text, None
    else:
        return None, (response.text, response.status_code)
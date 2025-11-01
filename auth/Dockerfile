FROM python:3.12-slim-bullseye

RUN apt-get update \
  && apt-get install -y --no-install-recommends --no-install-suggests \
  build-essential libpq-dev pkg-config \
  && pip install --no-cache-dir --upgrade pip

WORKDIR /app


# DOCKER VERSION

# COPY ./requirements.txt /app


# RUN pip install --no-cache-dir --requirement /app/requirements.txt

# COPY . /app

# EXPOSE 5050

# CMD [ "python3", "server.py"]



# DOCKER COMPOSE VERSION

COPY ./auth/requirements.txt /app   

RUN pip install --no-cache-dir --requirement /app/requirements.txt

COPY ./auth /app

CMD [ "python3", "server.py"]

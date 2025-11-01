FROM python:3.12-slim-bullseye

RUN apt-get update \
  && apt-get install -y --no-install-recommends --no-install-suggests \
  build-essential \
  && pip install --no-cache-dir --upgrade pip

WORKDIR /app

# DOCKER VERSION

# COPY ./requirements.txt /app

# RUN pip install --no-cache-dir --requirement /app/requirements.txt

# COPY . /app

# CMD ["python3", "consumer.py"]


# DOCKER COMPOSE VERSION

COPY ./notification/requirements.txt /app   

RUN pip install --no-cache-dir --requirement /app/requirements.txt

COPY ./notification /app

CMD [ "python3", "consumer.py"]
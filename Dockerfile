FROM python:3.12-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      ffmpeg \
      build-essential \
      python3-dev \
      git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN pip install --no-cache-dir --upgrade pip

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

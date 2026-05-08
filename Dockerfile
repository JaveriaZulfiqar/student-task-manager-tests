FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    wget curl gnupg unzip \
    chromium chromium-driver \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

RUN pip install selenium pytest pytest-html

ENV PYTHONUNBUFFERED=1

WORKDIR /tests

# Use a Python base image
FROM python:3.11-slim

# Install system dependencies for Selenium and Chrome
RUN apt-get update && apt-get install -y \
    wget curl gnupg unzip chromium chromium-driver \
    --no-install-recommends && rm -rf /var/lib/apt/lists/*

# Install Python testing tools
RUN pip install selenium pytest pytest-html

# Set the working directory
WORKDIR /tests

# CRITICAL: Copy your test scripts into the container
COPY . /tests/

# The command to run when the container starts
CMD ["python3", "-m", "pytest", ".", "-v"]

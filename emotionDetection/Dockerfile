# syntax=docker/dockerfile:1

# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.10-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        git \
        cmake \
        wget \
        unzip \
        libopencv-dev \
        libssl-dev \
        libcurl4-openssl-dev \
        libpng-dev \
        libx11-dev \
        libgtk-3-dev \
        curl\
    && rm -rf /var/lib/apt/lists/*

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True

# Copy local code to the container image.
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

# Install production dependencies.
RUN pip install --default-timeout=1000 --no-cache-dir -r requirements.txt


# Download datasets
# RUN mkdir -p dataset
# RUN curl -L https://storage.googleapis.com/733_dataset/games.jl -o dataset/games.jl
# RUN curl -L https://storage.googleapis.com/733_dataset/reviews.jl -o dataset/reviews.jl

# Run the web service on container startup. Here we use the gunicorn
# webserver, with one worker process and 8 threads.
# For environments with multiple CPU cores, increase the number of workers
# to be equal to the cores available.
# Timeout is set to 0 to disable the timeouts of the workers to allow Cloud Run to handle instance scaling.
ENV PORT 8080
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 emotionDeepFace:app
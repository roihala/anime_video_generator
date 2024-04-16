# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Install necessary system dependencies
RUN apt-get update \
    && apt-get install -y git libgl1-mesa-glx libglib2.0-0 ffmpeg ruby-full build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install bundler for Ruby gems
RUN gem install bundler

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt for Python
RUN pip install --no-cache-dir --default-timeout=1800 -r requirements.txt

# Install any needed gems specified in Gemfile for Ruby
RUN bundle install

# Copy the credentials file into the container
COPY ./credentials/animax-419913-c556959c0ca6.json /secrets/credentials.json

# Set the environment variable to point to the credentials file
ENV GOOGLE_APPLICATION_CREDENTIALS /secrets/credentials.json

# Run uvicorn when the container launches for Python app using shell form to allow variable substitution
CMD uvicorn app:app --host 0.0.0.0 --port $PORT

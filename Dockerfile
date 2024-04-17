# Use the official Ruby image that supports Ruby 3.3
FROM ruby:3.3

# Install Python 3 (you might need to specify the version you want)
RUN apt-get update -yqq && \
    apt-get install -yqq python3-pip python3-dev python3-venv ffmpeg &&  \
    apt-get clean

RUN python3 -m venv /app/venv

# Activate virtual environment
ENV PATH="/app/venv/bin:$PATH"

# Set the working directory in the Docker container
WORKDIR /app

# Copy the Gemfile and Gemfile.lock into the image
COPY Gemfile Gemfile.lock ./

# Create an empty data directory
RUN mkdir -p /app/output

# Install Ruby gems
RUN gem install bundler -v '2.4.21' && bundle install

# Copy the Python requirements file
COPY requirements.txt /app

# Install Python packages
RUN pip3 install --default-timeout=1800 -r requirements.txt

# Copy the rest of your application's code
COPY . /app

EXPOSE 8000

# Copy the credentials file into the container
COPY ./credentials/animax-419913-c556959c0ca6.json /secrets/credentials.json

# Set the environment variable to point to the credentials file
ENV GOOGLE_APPLICATION_CREDENTIALS /secrets/credentials.json

# Command to run your Ruby file (change the filename as needed)
CMD uvicorn app:app --host 0.0.0.0 --port $PORT

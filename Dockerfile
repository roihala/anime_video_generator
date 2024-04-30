# Start with a lightweight Ruby image based on Debian Slim
FROM ruby:3.3-slim-bullseye

# Set the working directory in the Docker container
WORKDIR /app

# Install Python3, pip, ffmpeg, and necessary dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    ffmpeg \
    build-essential \
    python3-dev \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/* \
    && pip3 install --no-cache-dir --upgrade pip setuptools wheel

# Copy the Gemfile and Gemfile.lock into the image
COPY Gemfile Gemfile.lock ./

# Install Ruby gems
RUN gem install bundler -v '2.4.21' && bundle install

# Copy the Python requirements file
COPY requirements.txt .

# Install Python packages in the virtual environment
RUN pip install --no-cache-dir --default-timeout=1800 -r requirements.txt

# Copy the rest of your application's code
COPY . .

# Expose the port the app will run on
EXPOSE 8000

# Copy the credentials file into the container
COPY ./credentials/animax-419913-c556959c0ca6.json /secrets/credentials.json

# Set the environment variable to point to the credentials file
ENV GOOGLE_APPLICATION_CREDENTIALS /secrets/credentials.json

# Command to run your application
CMD ["uvicorn", "app:app", "--workers", "4", "--host", "0.0.0.0", "--port", "8080"]

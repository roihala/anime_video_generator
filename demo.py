import base64
from google.cloud import storage
from dotenv import load_dotenv

from src.manager import Manager

load_dotenv()  # This loads the variables from '.env' into the environment


def main():
    Manager().manage()


def list_buckets():
    """Lists all buckets."""
    storage_client = storage.Client()
    buckets = storage_client.list_buckets()
    for bucket in buckets:
        print(bucket.name)


def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

def encode_api_key(api_key):
    # Encode the API key
    encoded_key = base64.b64encode(api_key.encode())
    print("Encoded API Key:", encoded_key)

    # Since base64.b64encode() returns a bytes object, you might want to convert it to a string for easier use in headers or URLs
    encoded_key_str = encoded_key.decode()
    print("Encoded API Key (str):", encoded_key_str)


if __name__ == '__main__':
    main()
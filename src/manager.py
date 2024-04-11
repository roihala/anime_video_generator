import os
import time

import requests

from google.cloud import storage

from config import VIDEO_DIR_STRUCTURE, OUTPUT_DIR, NARRATION_FILE, DEBUG, DEMO_DIR, BASE_DIR, DEMO_DIR_NAME, \
    IMAGES_DIR, SRT_FILE
from src.log import log

from pathlib import Path

from src.narrator import Narrator
from src.script_generator import ScriptGenerator
from src.video_maker import VideoMaker

class InvalidStoryError(Exception):
    pass


class Manager:
    def __init__(self):
        self.video_dir: Path = None
        self.story_id = None
        self.images = []

        storage_client = storage.Client()
        self.bucket = storage_client.bucket(os.getenv('GCS_BUCKET_NAME'))

    def manage(self, story_images=None, script=None):
        # The init process of this function is flipped. shoud've created video_dir
        # and fetched story at first. But using story_id obtained from narration for ease
        # BECAUSE WE DON'T HAVE DB

        log.info("STEP 0 - Prepare images")

        log.info("STEP 1 - script")
        script = ScriptGenerator().generate() if not script else script

        log.info("STEP 2 - narration")

        narrator = Narrator()
        # TODO: get voice and not ''
        story_id, narration_url = narrator.narrate('', script)
        narrator.request_transcription()

        self.video_dir = Path(str(BASE_DIR / story_id)) if not DEBUG else Path(DEMO_DIR)
        self.story_id = story_id

        if not os.path.exists(self.video_dir):
            os.makedirs(os.path.join(self.video_dir), exist_ok=True)

        # Create each subdirectory
        for subdir in VIDEO_DIR_STRUCTURE:
            os.makedirs(os.path.join(self.video_dir, subdir), exist_ok=True)

        self._fetch_narration(narration_url)
        try:
            if DEBUG:
                images_dir = DEMO_DIR / IMAGES_DIR
                self.images = [_ for _ in images_dir.iterdir() if _.is_file()]
            else:
                self._fetch_images(story_images)
        except Exception as e:
            log.error("Couldn't fetch story images, failing", e)
            raise InvalidStoryError("Couldn't fetch story images, failing", e)

        log.info("STEP 3 - video")
        videomaker = VideoMaker(story_id, self.video_dir)
        videomaker.make_video()
        # TODO: apply subtitles
        if not DEBUG:
            self._wait_for_captions()

        self.upload_dir_to_gcs()

    def _fetch_images(self, story_images):
        for index, image in enumerate(story_images):
            try:
                image_type = self._get_image_type(image)
                if image_type:
                    self._fetch_image(image, index, image_type)
            except Exception as e:
                log.warning(f"Couldn't download story image at: {image}", e)
        if not (10 >= len(self.images) <= 4):
            raise InvalidStoryError(f"Insufficient amount of story photos: {len(self.images)}")

    def upload_dir_to_gcs(self):
        """
        Uploads a directory to a GCS bucket, preserving the subdirectories structure.

        Parameters:
        - bucket_name (str): Name of the GCS bucket.
        - source_directory (str): The path to the directory to upload.
        - destination_blob_prefix (str): The prefix to add to blob names in the bucket.
        """
        for local_dir, _, files in os.walk(self.video_dir):
            for file in files:
                local_file_path = os.path.join(local_dir, file)
                relative_path = os.path.relpath(local_file_path, self.video_dir)
                blob_path = os.path.join(self.story_id if not DEBUG else DEMO_DIR_NAME, relative_path)

                blob = self.bucket.blob(blob_path)
                blob.upload_from_filename(local_file_path)
                log.info(f"Uploaded {local_file_path} to {blob_path}")

    def _fetch_image(self, url, index, image_type):
        """Download an image from a URL to a specified save path."""
        with requests.get(url, stream=True) as response:
            response.raise_for_status()
            local_path = self.video_dir / IMAGES_DIR / f'{index}.{image_type}'
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            self.images.append(local_path)

    def _get_image_type(self, url):
        """Check if the URL points to a valid image by checking its MIME type."""
        try:
            response = requests.head(url, allow_redirects=True)
            content_type = response.headers.get('Content-Type', '')
            if content_type.startswith('image/'):
                return content_type.split('/')[1]
        except requests.RequestException:
            return None

    def _wait_for_captions(self):
        # 18 attempts of 10 seconds = 3minutes
        for attempt in range(18):
            blob = self.bucket.blob(str(Path(self.story_id) / SRT_FILE))
            if blob.exists():
                log.info(f'{self.story_id}: FOUND CAPTIONS')
                return blob
            else:
                time.sleep(10)

        raise RuntimeError(f"{self.story_id}: Didn't get captions from webhook, failing")

    def _wait_for_narration_file(self, narration_url):
        retries = 0
        while retries < 30:
            try:
                response = requests.get(narration_url, stream=True)
                # Check if the URL is up (status code 200)
                if response.status_code == 200:
                    return response
                else:
                    # If the status code is not 200, prepare to retry after sleeping
                    raise requests.exceptions.RequestException
            except requests.exceptions.RequestException as e:
                log.warning(f"Attempt {retries + 1} failed. URL {narration_url} is not active. Retrying.", e)
                time.sleep(1)
                retries += 1

        # After max retries, if the URL is still not accessible, you might want to handle it differently.
        # Here, we're just printing a message. Depending on your application, you might raise an exception or return a default value.
        raise ValueError(f"Failed to fetch content from {narration_url}.")

    def _fetch_narration(self, narration_url):
        local_filename = self.video_dir / NARRATION_FILE
        response = self._wait_for_narration_file(narration_url)

        # Raise an exception if the request failed (HTTP error)
        response.raise_for_status()

        # Open a local file in binary write mode
        with open(local_filename, 'wb') as file:
            # Write the content of the response to the file
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)

        log.info(f"File downloaded successfully from {narration_url} to {local_filename}")
        return local_filename

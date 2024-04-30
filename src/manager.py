import random
import os
import time
import traceback

import requests

from google.cloud import storage

from config import VIDEO_DIR_STRUCTURE, OUTPUT_DIR, NARRATION_FILE, DEBUG, BASE_DIR, \
    IMAGES_DIR, SRT_FILE, GCS_URL_FORMAT, BACKGROUND_MUSIC_BUCKET_NAME, GCS_BUCKET_NAME, MUSIC_FILE, VIDEO_FOLDER, \
    VIDEO_FILE, logger_with_id, UNCAPTIONED_FILE
from pathlib import Path

from src.narrator import Narrator
from src.script_generator import ScriptGenerator
from src.video_maker import VideoMaker


class InvalidStoryError(Exception):
    pass


class Manager:
    def __init__(self):
        self.output_dir: Path = None
        self.story_id = None
        self.images = []

        storage_client = storage.Client()
        self.data_bucket = storage_client.bucket(GCS_BUCKET_NAME)
        self.music_bucket = storage_client.bucket(BACKGROUND_MUSIC_BUCKET_NAME)
        self.blob_path = None

    def manage(self, story_images=None, script=None):
        # The init process of this function is flipped. shoud've created video_dir
        # and fetched story at first. But using story_id obtained from narration for ease
        # BECAUSE WE DON'T HAVE DB

        logger_with_id.info("STEP 0 - Prepare images")

        logger_with_id.info("STEP 1 - script")
        script = ScriptGenerator().generate() if not script else script

        logger_with_id.info("STEP 2 - narration")

        narrator = Narrator()
        # TODO: get voice and not ''
        story_id, narration_url = narrator.narrate('', script)
        logger_with_id.extra['id'] = story_id
        narrator.request_transcription()

        self.output_dir = Path(str(BASE_DIR / story_id))
        self.story_id = story_id

        if not os.path.exists(self.output_dir):
            os.makedirs(os.path.join(self.output_dir), exist_ok=True)

        # Create each subdirectory
        for subdir in VIDEO_DIR_STRUCTURE:
            os.makedirs(os.path.join(self.output_dir, subdir), exist_ok=True)

        self._fetch_narration(narration_url)
        try:
            # if DEBUG:
            #     images_dir = DEMO_DIR / IMAGES_DIR
            #     self.images = [_ for _ in images_dir.iterdir() if _.is_file()]
            self._fetch_images(story_images)
        except Exception as e:
            logger_with_id.error(f"Couldn't fetch story images, failing: {str(e)} -> {traceback.print_exc()}")
            raise InvalidStoryError("Couldn't fetch story images, failing", e)

        logger_with_id.info("STEP 3 - video")
        music_file = self._fetch_random_music()
        videomaker = VideoMaker(story_id, self.output_dir, music_file)
        videomaker.make_video()

        logger_with_id.info("STEP 4 - captions")
        is_captions = False
        try:
            self._wait_for_captions()
            videomaker.burn_captions()
            is_captions = True
        except Exception as e:
            logger_with_id.error(f"Couldn't get captions: {str(e)} -> {traceback.print_exc()}")
        finally:
            self.upload_dir_to_gcs()

        if is_captions:
            return {'id': self.story_id, 'video_path': GCS_URL_FORMAT.format(os.path.join(self.story_id, videomaker.video_file_name))}
        else:
            return {'id': self.story_id, 'video_path': GCS_URL_FORMAT.format(os.path.join(self.story_id/UNCAPTIONED_FILE))}
            # TODO
            # return {'id': self.story_id, 'video_path': GCS_URL_FORMAT.format(self.story_id)}

    def _fetch_random_music(self) -> Path:
        try:
            # List all blobs in the bucket
            blobs = list(self.music_bucket.list_blobs())
            if not blobs:
                raise Exception("Couldn't find background music")

            # Select a random blob
            blob = random.choice(blobs)

            music_file = MUSIC_FILE.format(os.path.splitext(blob.name)[1].lstrip('.'))

            blob.download_to_filename(str(self.output_dir/music_file))
            return self.output_dir/music_file
        except Exception as e:
            raise RuntimeError("Couldn't download random music", e)

    def _fetch_images(self, story_images):
        for index, image in enumerate(story_images):
            try:
                image_type = self._get_image_type(image)
                if image_type:
                    self._fetch_image(image, index, image_type)
            except Exception as e:
                logger_with_id.warning(f"Couldn't download story image at: {image}: {str(e)} -> {traceback.print_exc()}")
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
        for local_dir, _, files in os.walk(self.output_dir):
            for file in files:
                local_file_path = os.path.join(local_dir, file)
                relative_path = os.path.relpath(local_file_path, self.output_dir)
                self.blob_path = os.path.join(self.story_id, relative_path)

                blob = self.data_bucket.blob(self.blob_path)
                blob.upload_from_filename(local_file_path)
                logger_with_id.info(f"Uploaded {local_file_path} to {self.blob_path}")

    def _fetch_image(self, url, index, image_type):
        """Download an image from a URL to a specified save path."""
        with requests.get(url, stream=True) as response:
            response.raise_for_status()
            local_path = self.output_dir / IMAGES_DIR / f'{index}.{image_type}'
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
        # 18 attempts of 10 seconds = 6minutes
        for attempt in range(36):
            try:
                blob = self.data_bucket.blob(str(Path(self.story_id) / SRT_FILE))
                if blob.exists():
                    logger_with_id.info(f'{self.story_id}: FOUND CAPTIONS')
                    blob_data = blob.download_as_bytes()

                    with open(str(self.output_dir / SRT_FILE), 'wb') as file:
                        file.write(blob_data)

                    return
            except Exception as e:
                logger_with_id.error(f"Error when trying to download blob data: {str(e)} -> {traceback.print_exc()}")
            time.sleep(10)
        if not os.path.exists(str(self.output_dir / SRT_FILE)):
            # TODO: originally if not blob
            raise RuntimeError("Couldn't find srt file")

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
                logger_with_id.warning(f"Attempt {retries + 1} failed. URL {narration_url} is not active. Retrying: {str(e)} -> {traceback.print_exc()}")
                time.sleep(1)
                retries += 1

        # After max retries, if the URL is still not accessible, you might want to handle it differently.
        # Here, we're just printing a message. Depending on your application, you might raise an exception or return a default value.
        raise ValueError(f"Failed to fetch content from {narration_url}.")

    def _fetch_narration(self, narration_url):
        local_filename = self.output_dir / NARRATION_FILE
        response = self._wait_for_narration_file(narration_url)

        # Raise an exception if the request failed (HTTP error)
        response.raise_for_status()

        # Open a local file in binary write mode
        with open(local_filename, 'wb') as file:
            # Write the content of the response to the file
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)

        logger_with_id.info(f"File downloaded successfully from {narration_url} to {local_filename}")
        return local_filename

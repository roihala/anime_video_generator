from src.blob_paths import BlobPaths
from src.log import log
import os
import random
import time

import cv2
import requests

from pydantic import BaseModel

from config import DEMO_DIR, VIDEO_DIR_STRUCTURE, OUTPUT_DIR,  NARRATION_FILE
from src.log import log

from pathlib import Path

from src.narrator import Narrator
from src.script_generator import ScriptGenerator
from src.video_maker import VideoMaker


class Manager:
    def __init__(self):
        self.video_dir = None

    def manage(self):
        log.info("STEP 0 - Prepare images")

        log.info("STEP 1 - script")
        script = ScriptGenerator().generate()

        log.info("STEP 2 - narration")

        narrator = Narrator()
        # TODO: get voice and not ''
        story_id, narration_url = narrator.narrate('', script)
        narrator.request_transcription()

        # TODO: bucket -> DEMO_DIR to default
        video_dir = Path(DEMO_DIR)

        if not os.path.exists(video_dir):
            os.makedirs(os.path.join(video_dir), exist_ok=True)

        # Create each subdirectory
        for subdir in VIDEO_DIR_STRUCTURE:
            os.makedirs(os.path.join(video_dir, subdir), exist_ok=True)

        video_dir = BlobPaths(story_id)

        log.info("STEP 3 - video")
        VideoMaker(self.video_dir).make_video()


    def _wait_for_narration_file(self, narration_url):
        retries = 0
        while retries < 30:
            try:
                response = requests.get(narration_url)
                # Check if the URL is up (status code 200)
                if response.status_code == 200:
                    return
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
        self._wait_for_narration_file(narration_url)
        # Send a GET request to the URL
        response = requests.get(narration_url, stream=True)

        # Raise an exception if the request failed (HTTP error)
        response.raise_for_status()

        # Open a local file in binary write mode
        with open(local_filename, 'wb') as file:
            # Write the content of the response to the file
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)

        log.info(f"File downloaded successfully from {narration_url} to {local_filename}")
        return local_filename

#!/usr/bin/env python3
#
#  main.py
#
#  Created by Eldar Eliav on 2023/05/11.
#

from os import path
from pathlib import Path

from log import log
from src.captions_generator import CaptionsGenerator
from src.script_generator import ScriptGenerator
from src.narrator import Narrator
from video_maker import VideoMaker
from dotenv import load_dotenv
import os
import assemblyai as aai

load_dotenv()  # This loads the variables from '.env' into the environment

DEBUG = os.getenv('DEBUG') == 'True'

DEMO_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'demo_output')
VOICE_NAME = 'Adam'
NARRATION_FILE = "awesome_voice.mp3"
SRT_FILE = "awesome_voice.srt"

VIDEO_DIR_STRUCTURE = ['images', 'video']


def generate_video(voice_name: str, video_dir: str):
    video_dir = Path(video_dir)
    # Prepare
    if not path.exists(video_dir):
        os.makedirs(os.path.join(video_dir), exist_ok=True)

    # Create each subdirectory
    for subdir in VIDEO_DIR_STRUCTURE:
        os.makedirs(os.path.join(video_dir, subdir), exist_ok=True)

    log.info("STEP 0 - Prepare images")

    log.info("STEP 1 - script")
    script = ScriptGenerator().generate()

    log.info("STEP 2 - narration")

    narrator = Narrator()
    # TODO: voice from our api
    narration_url = narrator.narrate(voice_name, script)
    narrator.request_transcription()

    # log.info("STEP 3 - video")
    # VideoMaker(video_dir, narration_url).make_video()


if __name__ == "__main__":
    generate_video(
        voice_name=VOICE_NAME,
        video_dir=DEMO_DIR
    )

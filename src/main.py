#!/usr/bin/env python3
#
#  main.py
#
#  Created by Eldar Eliav on 2023/05/11.
#

from os import path
from log import log
from script_generator import ScriptGenerator
from script_narration import ScriptNarration

from scripts.get_background_music import GetBackgroundMusic
from video_maker import VideoMaker
from dotenv import load_dotenv
import os

load_dotenv()  # This loads the variables from '.env' into the environment

DEBUG = os.getenv('DEBUG') == 'True'

DESTINATION_DIR = "./demo_output/"
VOICE_NAME = 'Adam'
VOICE_FILE = "awesome_voice.mp3"
VIDEO_DIR_STRUCTURE = ['images', 'video']


def generate_video(voice_name: str, video_dir: str):
    # Prepare
    if not path.exists(video_dir):
        os.makedirs(os.path.join(video_dir), exist_ok=True)

    # Create each subdirectory
    for subdir in VIDEO_DIR_STRUCTURE:
        os.makedirs(os.path.join(video_dir, subdir), exist_ok=True)

    if os.getenv('DEBUG'):
        # GetBackgroundMusic().generate()
        # return
        pass
    log.info("STEP 0 - Prepare images")
    # TODO: image getter
    # images_path_list = [r"C:\Users\RoiHa\PycharmProjects\anime_video_generator\demo_output\007.jpg", r"C:\Users\RoiHa\PycharmProjects\anime_video_generator\demo_output\011.jpg", r"C:\Users\RoiHa\PycharmProjects\anime_video_generator\demo_output\018.jpg", r"C:\Users\RoiHa\PycharmProjects\anime_video_generator\demo_output\028.jpg"]


    log.info("STEP 1 - script")
    script = ScriptGenerator().generate()

    log.info("STEP 2 - narration")
    voice_file_path = path.join(video_dir, VOICE_FILE)
    ScriptNarration().narrate(voice_name, script, voice_file_path)

    # log.info("STEP 3 - captions")
    # generated_images_path_list = CaptionsGenerator().generate_captions(
    #     captions_string = captions,
    #     destination_dir = destination_dir,
    #     is_crop_to_ratio_16_9 = True
    # )

    log.info("STEP 4 - video")
    VideoMaker(video_dir, voice_file_path).make_video()


if __name__ == "__main__":
    generate_video(
        voice_name = VOICE_NAME,
        video_dir= DESTINATION_DIR
    )

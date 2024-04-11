# config.py
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()  # This loads the variables from '.env' into the environment

DEBUG = os.getenv('DEBUG', 'False') == 'True'
BASE_DIR = Path(os.path.dirname(__file__)) / 'output'
DEMO_DIR_NAME = 'demo_output'
DEMO_DIR = Path(os.path.dirname(__file__)) / DEMO_DIR_NAME
VOICE_NAME = 'Adam'

# Lib
LIB_DIRECTORY = Path(os.path.dirname(__file__)) / 'lib'
AUDIO_LIBRARY = LIB_DIRECTORY / 'background_music'
TRANSITION_SOUND_EFFECT = LIB_DIRECTORY / 'sound FX' / 'Whoosh Sound Effect 01.mp3'
OLD_MAKER_FILE = LIB_DIRECTORY / 'maker.rb'

# Ruby
RUBY_DIR = LIB_DIRECTORY / 'ruby'
VIDEO_MAKER = RUBY_DIR / 'make_video.rb'
SCENE_MAKER = RUBY_DIR / 'make_scene.rb'
SHARP_CUT_MAKER = RUBY_DIR / 'sharp_cut.rb'
FILE_LIST = 'file_list.txt'

# Current video subdirectory
OUTPUT_DIR = 'output'
IMAGES_DIR = 'images'
SHARP_CUT_FILE_FORMAT = 'sharpcut_{0}_{1}.mp4'
SCENE_FILE_FORMAT = 'scene{index}.mp4'
FIRST_FRAME_PATH = 'scene{}_first_frame.jpg'
LAST_FRAME_PATH = 'scene{}_last_frame.jpg'
NARRATION_FILE = "awesome_voice.mp3"
SRT_FILE = "awesome_voice.srt"
VIDEO_FILE = 'video-{0}.mp4'

VIDEO_DIR_STRUCTURE = ['images', 'video']

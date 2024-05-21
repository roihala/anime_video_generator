#
#
#
# config.py
import logging
import os
import sys
from pathlib import Path

import pytest
from dotenv import load_dotenv

load_dotenv()  # This loads the variables from '.env' into the environment

DEBUG = os.getenv('DEBUG', 'False') == 'True'
OUT_DIR = Path(__file__).parent / 'output' if DEBUG else Path('/mnt/data') / 'output'
VOICE_NAME = 'Adam'

# Lib
LIB_DIRECTORY = Path(os.path.dirname(__file__)) / 'lib'
AUDIO_LIBRARY = LIB_DIRECTORY / 'background_music'
TRANSITION_SOUND_EFFECT = LIB_DIRECTORY / 'sound_FX' / 'whoosh_sound.mp3'
OLD_MAKER_FILE = LIB_DIRECTORY / 'maker.rb'
TOONTUBE_LOGO = LIB_DIRECTORY / 'assets' / 'black_logo.mp4'
VOICES_JSON = LIB_DIRECTORY / 'assets' / 'voices.json'

# Ruby
RUBY_DIR = LIB_DIRECTORY / 'ruby'
VIDEO_MAKER = RUBY_DIR / 'make_video.rb'
BURN_CAPTIONS = RUBY_DIR / 'burn_captions.rb'
SCENE_MAKER = RUBY_DIR / 'make_scene.rb'
SHARP_CUT_MAKER = RUBY_DIR / 'sharp_cut.rb'
FILE_LIST = 'file_list.txt'

# Current video subdirectory
OUTPUT_DIR = 'output'
IMAGES_DIR = 'images'
SHARP_CUT_FILE_FORMAT = 'scenes/sharpcut_{0}_{1}.mp4'
SCENES_FOLDER = 'scenes'
SCENE_FILE_FORMAT = 'scenes/scene{index}.mp4'
FIRST_FRAME_PATH = 'scenes/scene{}_first_frame.jpg'
LAST_FRAME_PATH = 'scenes/scene{}_last_frame.jpg'
IMAGE_FILE_FORMAT = 'image'
NARRATION_FILE = "awesome_voice.mp3"
MUSIC_FILE = "awesome_music.{}"
SRT_FILE = "awesome_voice.srt"
ASS_FILE = "awesome_voice.ass"
UNCAPTIONED_FILE = 'uncaptioned_video.mp4'
VIDEO_FILE = 'video/video-{0}.mp4'
VIDEO_DIR_STRUCTURE = ['images', 'video']

# URLs
GCS_URL_FORMAT = 'https://storage.googleapis.com/animax_data1/{0}'

# GCP
PROJECT_ID = 'animax-423606'
GCS_BUCKET_NAME = 'animax_data1'
BACKGROUND_MUSIC_BUCKET_NAME = 'animax_music1'
API_REQUEST_TOPIC = 'api-request-topic' if not DEBUG else 'api-request-debug'
API_REQUEST_SUBSCRIPTION = 'api-request-topic-sub' if not DEBUG else 'api-request-debug-sub'
BRIDGE_TOPIC = 'bridge' if not DEBUG else 'bridge-debug'
BRIDGE_SUBSCRIPTION = 'bridge-sub' if not DEBUG else 'bridge-debug-sub'

# Logic
MINIMUM_SCENES = 4
MAXIMUM_SCENES = 7
MINIMUM_SCENE_DURATION = 1.5 # In seconds

# Video creation
# Frame duration per 60 fps = 1 / 60(frames) ≈ 16.67
FRAME_DURATION = 1 / 60
SHARP_CUT_FRAME_DURATION = 12
MAX_VIDEO_DURATION = 40
DEFAULT_MUSIC_GAIN = -18 # In decibels
DEFAULT_NARRATION_GAIN = -10 # In decibels
SCALE_MODES = ['pad', 'pan']

class CustomLoggerAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        return f'[ID: {self.extra["id"]}] {msg}', kwargs


class LoggerWithId:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(LoggerWithId, cls).__new__(cls)
            cls._instance.logger = None
            cls._instance.id = None
        return cls._instance

    def __init__(self, _id='unknown'):
        # Only initialize the logger if it hasn't been initialized or if the ID has changed
        if self.logger is None or self.id != _id:
            self.set_id(_id)

    def __getattr__(self, item):
        # Ensure that self.logger is fully set up before trying to access its attributes
        if self.logger is not None:
            attr = getattr(self.logger, item)
            if callable(attr):
                return attr
        raise AttributeError(f"'LoggerWithId' object or 'logger' has no attribute '{item}'")

    def set_id(self, _id='unknown'):
        self.id = _id

        logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(levelname)s - %(message)s',
                handlers=[logging.StreamHandler(sys.stdout)]
            )

        # Create a logger instance only once
        l = logging.getLogger("animax-logger")
        self.logger = CustomLoggerAdapter(l, {'id': _id})

logger = LoggerWithId()

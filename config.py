#
#
#
# config.py
import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()  # This loads the variables from '.env' into the environment

DEBUG = os.getenv('DEBUG', 'False') == 'True'
BASE_DIR = Path(__file__).parent / 'output'
VOICE_NAME = 'Adam'

# Lib
LIB_DIRECTORY = Path(os.path.dirname(__file__)) / 'lib'
AUDIO_LIBRARY = LIB_DIRECTORY / 'background_music'
TRANSITION_SOUND_EFFECT = LIB_DIRECTORY / 'sound FX' / 'Whoosh Sound Effect 01.mp3'
OLD_MAKER_FILE = LIB_DIRECTORY / 'maker.rb'

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
SHARP_CUT_FILE_FORMAT = 'sharpcut_{0}_{1}.mp4'
SCENE_FILE_FORMAT = 'scene{index}.mp4'
FIRST_FRAME_PATH = 'scene{}_first_frame.jpg'
LAST_FRAME_PATH = 'scene{}_last_frame.jpg'
NARRATION_FILE = "awesome_voice.mp3"
MUSIC_FILE = "awesome_music.{}"
SRT_FILE = "awesome_voice.srt"
UNCAPTIONED_FILE = 'uncaptioned_video.mp4'
VIDEO_FOLDER = 'video'
VIDEO_FILE = 'video/video-{0}.mp4'
VIDEO_DIR_STRUCTURE = ['images', 'video']

# URLs
GCS_URL_FORMAT = 'https://storage.googleapis.com/animax_data/{0}'

# Buckets
GCS_BUCKET_NAME = 'animax_data'
BACKGROUND_MUSIC_BUCKET_NAME = 'animax_music'


class CustomLoggerAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        return '[ID: %s] %s' % (self.extra['id'], msg), kwargs

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger("animax-logger")
logger_with_id = CustomLoggerAdapter(logger, {'id': 'unknown'})

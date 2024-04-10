# config.py
import os
from pathlib import Path

DEBUG = os.getenv('DEBUG', 'False') == 'True'

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DEMO_DIR = os.path.join(BASE_DIR, 'demo_output')
VOICE_NAME = 'Adam'
NARRATION_FILE = "awesome_voice.mp3"
SRT_FILE = "awesome_voice.srt"


# Lib
LIB_DIRECTORY = Path(os.path.dirname(__file__)) / 'lib'
AUDIO_LIBRARY = LIB_DIRECTORY / 'background_music'
TRANSITION_SOUND_EFFECT = LIB_DIRECTORY / 'sound FX' / 'Whoosh 08.wav'
OLD_MAKER_FILE = LIB_DIRECTORY / 'maker.rb'

# Ruby
RUBY_DIR = LIB_DIRECTORY / 'ruby'
VIDEO_MAKER = RUBY_DIR / 'make_video.rb'
SCENE_MAKER = RUBY_DIR / 'make_scene.rb'
SHARP_CUT_MAKER = RUBY_DIR / 'sharp_cut.rb'

# Current video subdirectory
OUTPUT_DIR = 'output'
IMAGES_DIR = 'images'
SHARP_CUT_FILE_FORMAT = 'sharpcut_{0}_{1}.mp4'
SCENE_FILE_FORMAT = 'scene{index}.mp4'
FIRST_FRAME_PATH = 'scene{}_first_frame.jpg'
LAST_FRAME_PATH = 'scene{}_last_frame.jpg'
FILE_LIST = 'file_list.txt'

VIDEO_DIR_STRUCTURE = ['images', 'video']

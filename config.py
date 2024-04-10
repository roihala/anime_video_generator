# config.py
import os

DEBUG = os.getenv('DEBUG', 'False') == 'True'

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DEMO_DIR = os.path.join(BASE_DIR, 'demo_output')
VOICE_NAME = 'Adam'
NARRATION_FILE = "awesome_voice.mp3"
SRT_FILE = "awesome_voice.srt"

VIDEO_DIR_STRUCTURE = ['images', 'video']

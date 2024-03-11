#
#  video_maker.py
#
#  Created by Eldar Eliav on 2023/05/13.
#
import os
import random

from log import log
from pydub import AudioSegment
import soundfile as sf
import pyloudnorm as pyln
from src.animax_exception import AnimaxException, BacgkgroundMusicException


RUBY_DIR_PATH = os.path.join(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'lib'), 'ruby')
AUDIO_LIBRARY = os.path.join(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'lib'), 'background_music')

MAKER_SCRIPT_PATH = os.path.join(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'lib'), 'maker.rb')
SHARP_CUT_SCRIPT_PATH = os.path.join(RUBY_DIR_PATH, 'sharp_cut.rb')
# Default target loudness, in decibels
DEFAULT_TARGET_LOUDNESS = -8

class VideoMaker:
    def __init__(self, video_dir: str, voice_file_path: str, video_file_path: str, srt_file_path: str):
        self.video_dir = video_dir
        self.voice_file_path = voice_file_path
        self.video_file_path = video_file_path
        self.srt_file_path = srt_file_path

    def make_video(self):
        log.info("generating video...")

        images_dir = os.path.join(self.video_dir, 'images')
        images_list = [os.path.join(images_dir, f) for f in os.listdir(images_dir) if os.path.isfile(os.path.join(images_dir, f))]
        video_duration = self._get_audio_duration(self.voice_file_path)
        background_audio, volume_adjustment = self._get_background_audio(video_duration)
        slide_duration = self._calculate_slide_daration(
            audio_duration= video_duration,
            number_of_images = len(images_list)
        )

        # self.sharp_cut(images_list[0:2])
        # return
        images_string = " ".join(images_list)

        cmd = f'ruby {MAKER_SCRIPT_PATH} {images_string} {self.video_file_path} --size=1080x1920 --slide-duration={slide_duration} --fade-duration=1 --zoom-rate=0.2 --zoom-direction=random --scale-mode=pad --audio_narration={self.voice_file_path} --audio_music="{background_audio}" --audio_music_volume_adjustment={volume_adjustment} -y'

        log.info(f'ruby command {cmd}')
        os.system(cmd)

        # TODO: how to tell if it was successful?
        log.info(f"video generated : {self.video_file_path}")

    def sharp_cut(self, images):
        images_string = " ".join(images)
        transition_file_path = os.path.join(self.video_dir, 'sharp_cut.mp4')
        cmd = f'ruby {SHARP_CUT_SCRIPT_PATH} {images_string} {transition_file_path}'

        log.info(f'ruby command {cmd}')
        os.system(cmd)
        log.info(f"video generated : {self.video_file_path}")


    # private methods
    def _calculate_slide_daration(self, audio_duration: int, number_of_images: int) -> float:
        return audio_duration / number_of_images

    def _get_audio_duration(self, mp3_audio_file_path: str) -> int:
        audio_object = AudioSegment.from_file(mp3_audio_file_path, format="mp3")
        return audio_object.duration_seconds

    def _get_background_audio(self, video_duration: int) -> (str, float):
        """

        :param video_duration:
        :return: file_path, volume to adjust in decibels
        """
        for _ in range(10):
            try:
                random_path = os.path.join(AUDIO_LIBRARY, random.choice(os.listdir(AUDIO_LIBRARY)))
                audio = AudioSegment.from_file(random_path)
                if audio.duration_seconds >= video_duration:
                    return random_path, self._get_background_audio_volume_adjustment(random_path)
            except Exception as e:
                log.warning(f"Couldn't fetch background audio in {random_path if 'random_path' in locals() else _}", e)
        raise BacgkgroundMusicException("Couldn't find background music")

    def _get_background_audio_volume_adjustment(self, file_path) -> float:
        # measure_loudness
        data, rate = sf.read(file_path)  # Read audio file

        meter = pyln.Meter(rate)  # create BS.1770 meter
        loudness = meter.integrated_loudness(data)  # measure loudness

        gain = DEFAULT_TARGET_LOUDNESS - loudness
        return gain

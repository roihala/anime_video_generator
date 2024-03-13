#
#  video_maker.py
#
#  Created by Eldar Eliav on 2023/05/13.
#
import os
import random

from pydantic import BaseModel

from log import log
from pydub import AudioSegment
import soundfile as sf
import pyloudnorm as pyln
from types import SimpleNamespace
from src.animax_exception import AnimaxException, BacgkgroundMusicException

from pathlib import Path

# Lib
LIB_DIRECTORY = Path(os.path.dirname(os.path.dirname(__file__))) / 'lib'
AUDIO_LIBRARY = LIB_DIRECTORY / 'background_music'
OLD_MAKER_FILE = LIB_DIRECTORY / 'maker.rb'

# Ruby
RUBY_DIR = LIB_DIRECTORY / 'ruby'
SCENE_MAKER_FILE = RUBY_DIR / 'make_scene.rb'
SHARP_CUT_FILE = RUBY_DIR / 'sharp_cut.rb'

# Current video subdirectory
OUTPUT_DIR = 'output'
IMAGES_DIR = 'images'
SHARP_CUT_FILE_FORMAT = 'sharpcut_{index0}_{index1}.mp4'
SCENE_FILE_FORMAT = 'scene{index}.mp4'

# Default target loudness, in decibels
DEFAULT_TARGET_LOUDNESS = -8
SCALE_MODES = ['pad', 'pan']


class Slide(BaseModel):
    img_path: Path
    output_path: Path
    duration: float


class VideoMaker:
    def __init__(self, video_dir: Path, narration_file_path: Path):
        self.video_dir = video_dir
        self.output_dir: Path = video_dir / OUTPUT_DIR
        self.narration_file_path = narration_file_path

        self.slides_dict = {i: Slide(img_path=self.video_dir / IMAGES_DIR / f, duration=random.uniform(3, 4),
                                     output_path=self.output_dir / SCENE_FILE_FORMAT.format(index=i)) for i, f in
                            enumerate(os.listdir(self.video_dir / IMAGES_DIR))}

        # TODO
        video_file_path = video_dir / "video/video.mp4"
        self.video_file_path = video_file_path

    def make_video(self):
        self.make_scenes()
        # self.make_cuts('x', 'y')
        # self.old_video_maker()
        # return

    def make_scenes(self):
        for i, slide in self.slides_dict.items():
            cmd = (
                f'ruby {SCENE_MAKER_FILE} {slide.img_path} {slide.output_path} --slide-duration={slide.duration} '
                f'--zoom-rate=0.1 --zoom-direction=random --scale-mode={random.choice(SCALE_MODES)} -y')

            log.info(f'ruby command {cmd}')
            os.system(cmd)

    def make_cuts(self, scene_1, scene_2):
        # for i,  in enumerate(slides_dict.items()):

        transition_file_path = os.path.join(self.video_dir, 'sharp_cut.mp4')
        images_dir = self.video_dir / IMAGES_DIR
        slides_dict = {os.path.join(images_dir, f): random.uniform(3, 4) for f in os.listdir(images_dir)
                       if os.path.isfile(os.path.join(images_dir, f))}
        images_string = " ".join(list(slides_dict.keys())[0:2])

        cmd = f'ruby {SHARP_CUT_FILE} {images_string} {transition_file_path}'

        log.info(f'ruby command {cmd}')
        os.system(cmd)
        log.info(f"video generated : {self.video_file_path}")

    def old_video_maker(self):
        log.info("generating video...")

        images_dir = os.path.join(self.video_dir, 'images')
        images_list = [os.path.join(images_dir, f) for f in os.listdir(images_dir) if
                       os.path.isfile(os.path.join(images_dir, f))]
        video_duration = self._get_audio_duration(self.narration_file_path)
        background_audio, volume_adjustment = self._get_background_audio(video_duration)
        slide_duration = self._calculate_slide_daration(
            audio_duration=video_duration,
            number_of_images=len(images_list)
        )

        # self.sharp_cut(images_list[0:2])
        # return

        images_string = " ".join(images_list)

        cmd = f'ruby {OLD_MAKER_FILE} {images_string} {self.video_file_path} --size=1080x1920 --slide-duration={slide_duration} --fade-duration=1 --zoom-rate=0.2 --zoom-direction=random --scale-mode=pad --audio_narration={self.narration_file_path} --audio_music="{background_audio}" --audio_music_volume_adjustment={volume_adjustment} -y'
        log.info(f'ruby command {cmd}')
        os.system(cmd)

        # TODO: how to tell if it was successful?
        log.info(f"video generated : {self.video_file_path}")

    def sharp_cut(self, images):
        images_string = " ".join(images)
        transition_file_path = os.path.join(self.video_dir, 'sharp_cut.mp4')
        cmd = f'ruby {SHARP_CUT_FILE} {images_string} {transition_file_path}'

        log.info(f'ruby command {cmd}')
        os.system(cmd)
        log.info(f"video generated : {self.video_file_path}")

    # private methods
    def _calculate_slide_daration(self, audio_duration: int, number_of_images: int) -> float:
        # TODO: return dynamic slide duration
        return 4

        # return audio_duration / number_of_images

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

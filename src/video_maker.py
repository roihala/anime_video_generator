#
#  video_maker.py
#
#  Created by Eldar Eliav on 2023/05/13.
#
import os
import random
import subprocess
import time

import cv2
import requests

from pydantic import BaseModel

from config import SCENE_MAKER, SHARP_CUT_FILE_FORMAT, SHARP_CUT_MAKER, \
    FILE_LIST, TRANSITION_SOUND_EFFECT, LAST_FRAME_PATH, FIRST_FRAME_PATH, IMAGES_DIR, SCENE_FILE_FORMAT, AUDIO_LIBRARY, \
    VIDEO_MAKER, NARRATION_FILE, VIDEO_FILE, BURN_CAPTIONS, UNCAPTIONED_FILE, VIDEO_FOLDER, SRT_FILE, MUSIC_FILE, \
    logger_with_id, DEBUG, TOONTUBE_LOGO
from pydub import AudioSegment
import soundfile as sf
import pyloudnorm as pyln
from types import SimpleNamespace
from src.animax_exception import AnimaxException, BacgkgroundMusicException
from google.cloud import storage
from pathlib import Path

# Default target loudness, in decibels
DEFAULT_TARGET_LOUDNESS = -8
SCALE_MODES = ['pad', 'pan']


# Frame duration per 60 fps = 1 / 60(frames) ≈ 16.67
FRAME_DURATION = 1 / 60
SHARP_CUT_FRAME_DURATION = 12
MAX_VIDEO_DURATION = 30


class Slide(BaseModel):
    index: int
    scene_path: Path
    scene_duration: float
    img_path: Path = None
    transition_path: Path = None
    transition_duration: float = None
    first_frame_path: Path = None
    last_frame_path: Path = None


class VideoMaker:
    def __init__(self, story_id, output_dir: Path, music_file: Path, slides=None):
        self.music_file = music_file
        self.story_id = story_id
        self.output_dir = output_dir
        self.output_dir: Path = output_dir
        self.video_file_name = VIDEO_FILE.format(story_id)
        self.video_file_path = output_dir / self.video_file_name
        self.narration_file = output_dir / NARRATION_FILE

        self.slides = []
        if slides and DEBUG:
            self.slides = slides
        else:
            self._generate_slides()

    def make_video(self):
        self.make_scenes()
        self.make_transitions()
        # Adding toontube logo slide
        self.slides.append(
            Slide(index=len(self.slides),
                  scene_path=TOONTUBE_LOGO,
                  scene_duration=2.0))
        self.connect_all()

    def burn_captions(self):
        cmd = [f'ruby', f'{BURN_CAPTIONS}',
               f'--input-file', f'{self.output_dir / UNCAPTIONED_FILE}',
               f'--srt-file', f'{self.output_dir / SRT_FILE}',
               f'--output_file', f'{self.video_file_path}']

        logger_with_id.info(f'ruby command {" ".join(cmd)}')
        result = subprocess.run(cmd, capture_output=True, text=True)
        logger_with_id.info(f"Command output: {result.stderr}")

    def make_scenes(self):
        for i, slide in enumerate(self.slides):
            cmd = [
                f'ruby', f'{SCENE_MAKER}', f'{slide.img_path}', f'{slide.scene_path}', f'--slide-duration={slide.scene_duration}',
                f'--zoom-rate=0.1', '--zoom-direction=random', f'--scale-mode={random.choice(SCALE_MODES)}', '-y']

            logger_with_id.info(f'ruby command {" ".join(cmd)}')
            result = subprocess.run(cmd, capture_output=True, text=True)
            logger_with_id.info(f"Command output: {result.stderr}")

    def make_transitions(self):
        for i, slide in enumerate(self.slides[0:-1]):
            last_frame = self.extract_frame(slide, is_last=True)
            first_frame = self.extract_frame(self.slides[i+1], is_last=False)
            slide.transition_path = self.output_dir / SHARP_CUT_FILE_FORMAT.format(i, i + 1)

            # This calculation is specifically for sharp cut, other transitions will have to be calculated differently
            slide.transition_duration = (FRAME_DURATION * SHARP_CUT_FRAME_DURATION)
            cmd = [f'ruby', f'{SHARP_CUT_MAKER}', f'{last_frame}', f'{first_frame}', f'{slide.transition_path}']
            logger_with_id.info(f'ruby command {" ".join(cmd)}')
            result = subprocess.run(cmd, capture_output=True, text=True)
            logger_with_id.info(f"Command output: {result.stderr}")

    def connect_all(self):
        # Generate the necessary attributes for the ruby file:
        # - file_list.txt file that holds all the video to concatenate
        # - corresponding list of durations
        durations = []
        with open(self.output_dir / FILE_LIST, 'w') as file:
            for slide in self.slides:
                file.write(f"file '{slide.scene_path}'\n")
                durations.append(slide.scene_duration)

                if slide.transition_path:
                    file.write(f"file '{slide.transition_path}'\n")
                    durations.append(slide.transition_duration)

        volume_adjustment = self._get_background_audio_volume_adjustment(str(self.music_file))
        cmd = [f'ruby',
               f'{VIDEO_MAKER}',
               f'--file_list', f'{self.output_dir / FILE_LIST}',
               f'--durations', f'{",".join([str(_) for _ in durations])}',
               f'--background_music', f'{self.music_file}',
               f'--music-volume-adjustment', f'{volume_adjustment}',
               f'--narration-audio', f'{self.narration_file}',
               f'--transition-sound-effect', f'{TRANSITION_SOUND_EFFECT}',
               f'--output_file', f'{self.output_dir / UNCAPTIONED_FILE}']

        logger_with_id.info(f'ruby command {" ".join(cmd)}')
        result = subprocess.run(cmd, capture_output=True, text=True)
        logger_with_id.info(f"Command output: {result.stderr} ||| {result.stdout}")

    def sharp_cut(self, images):
        images_string = " ".join(images)
        transition_file_path = os.path.join(self.output_dir, 'sharp_cut.mp4')
        cmd = [f'ruby', f'{SHARP_CUT_MAKER}', f'{images_string}', f'{transition_file_path}']

        logger_with_id.info(f'ruby command {" ".join(cmd)}')
        result = subprocess.run(cmd, capture_output=True, text=True)
        logger_with_id.info(f"Command output: {result.stderr}")

    def extract_frame(self, slide: Slide, is_last=True):
        # if not is_last - will extract first frame
        video_path = slide.scene_path
        # Capture the video
        cap = cv2.VideoCapture(str(video_path))
        # Check if video opened successfully
        if not cap.isOpened():
            logger_with_id.warning("Error opening video file")
            return
        if is_last:
            image_path = self.output_dir / LAST_FRAME_PATH.format(slide.index)

            # Get the total number of frames in the video
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            frame_index = total_frames - 1
        else:
            image_path = self.output_dir / FIRST_FRAME_PATH.format(slide.index)
            frame_index = 0

        # Set the current frame position to the last frame
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)

        # Read the last frame
        ret, frame = cap.read()

        # Check if the frame was captured successfully
        if ret:
            # Save the frame as an image
            cv2.imwrite(str(image_path), frame)
            if is_last:
                slide.last_frame_path = image_path
            else:
                slide.first_frame_path = image_path
            return image_path
        else:
            logger_with_id.warning("Error extracting the last frame")

        # Release the video capture object
        cap.release()
        cv2.destroyAllWindows()

    def _generate_slides(self):
        # Generating slides with random durations
        # Each slide is an image

        video_duration = self._get_audio_duration(str(self.narration_file))
        if video_duration > MAX_VIDEO_DURATION:
            raise ValueError(f"Video duration is too long - {self.narration_file}")

        scenes = os.listdir(self.output_dir / IMAGES_DIR)

        # Randomly disparse scene durations
        durations = [random.random() for _ in range(len(scenes))]
        durations = [d / sum(durations) * video_duration for d in durations]
        i = 0
        for i in range(len(scenes)):
            self.slides.append(
                Slide(index=i,
                      img_path=self.output_dir / IMAGES_DIR / scenes[i],
                      scene_duration=durations[i],
                      scene_path=self.output_dir / SCENE_FILE_FORMAT.format(index=i))
            )

    def _get_audio_duration(self, mp3_audio_file_path: str) -> int:
        audio_object = AudioSegment.from_file(mp3_audio_file_path, format="mp3")
        return audio_object.duration_seconds

    @staticmethod
    def _get_background_audio_volume_adjustment(file_path: str) -> float:
        # measure_loudness
        data, rate = sf.read(file_path)  # Read audio file

        meter = pyln.Meter(rate)  # create BS.1770 meter
        loudness = meter.integrated_loudness(data)  # measure loudness
        gain = DEFAULT_TARGET_LOUDNESS - loudness
        return gain

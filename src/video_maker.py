#
#  video_maker.py
#
#  Created by Eldar Eliav on 2023/05/13.
#
import datetime
import logging
import os
import random
import subprocess
import time
from asyncio import as_completed
from concurrent.futures import ThreadPoolExecutor
from typing import List, Tuple, Dict

from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR, EVENT_JOB_ADDED, EVENT_JOB_REMOVED
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.date import DateTrigger
from kubernetes import client, config
from kubernetes.stream import stream
import subprocess

import cv2
import requests

from pydantic import BaseModel

from config import SCENE_MAKER, SHARP_CUT_FILE_FORMAT, SHARP_CUT_MAKER, \
    FILE_LIST, TRANSITION_SOUND_EFFECT, LAST_FRAME_PATH, FIRST_FRAME_PATH, IMAGES_DIR, SCENE_FILE_FORMAT, AUDIO_LIBRARY, \
    VIDEO_MAKER, NARRATION_FILE, VIDEO_FILE, BURN_CAPTIONS, UNCAPTIONED_FILE, MUSIC_FILE, \
    DEBUG, TOONTUBE_LOGO, logger, MINIMUM_SCENES, SCENES_FOLDER, MINIMUM_SCENE_DURATION, ASS_FILE, FRAME_DURATION, \
    SHARP_CUT_FRAME_DURATION, SCALE_MODES, MAX_VIDEO_DURATION, DEFAULT_MUSIC_GAIN, DEFAULT_NARRATION_GAIN
from pydub import AudioSegment
import soundfile as sf
import pyloudnorm as pyln
from pathlib import Path

from src.scene_creator import SceneCreator
from src.pydantic_models.slide import Slide, SlideJob


class VideoMaker:
    def __init__(self, story_id, output_dir: Path, music_file: Path, slides=None):
        self.music_file = music_file
        self.story_id = story_id
        self.output_dir = output_dir
        self.output_dir: Path = output_dir
        self.video_file_name = VIDEO_FILE.format(story_id)
        self.video_file_path = output_dir / self.video_file_name
        self.narration_file = output_dir / NARRATION_FILE

        if not os.path.exists(output_dir / SCENES_FOLDER):
            os.makedirs(output_dir / SCENES_FOLDER)

        self.slides = []
        if slides and DEBUG:
            self.slides = slides
        else:
            self._generate_slides()
            logger.info(f"Successfully generated slides: {self.slides}")

    def make_video(self):
        scene_creator = SceneCreator(self.output_dir, self.slides)
        slide_jobs = scene_creator.run()
        success = sum([1 for sj in slide_jobs.values() if sj.is_success ])
        results = {'SUCCESS': f'{success}/{len(slide_jobs)}'}
        logger.info(f"Scene creator finished, these are the results: {results} | {slide_jobs}")
        scenes, transitions = self._count_produced(slide_jobs)
        if scenes < MINIMUM_SCENES:
            raise RuntimeError(f"Couldn't produce enough scenes, produced {scenes} scenes ({transitions}) transitions | {slide_jobs}")

        self.connect_all()
        self.slides.append(
            Slide(index=len(self.slides),
                  scene_path=TOONTUBE_LOGO,
                  scene_duration=2.0))

    def _count_produced(self, slide_jobs: Dict[str, SlideJob]):
        scenes, transitions = 0, 0
        for slide_job in slide_jobs.values():
            if slide_job.is_success:
                if slide_job.is_transition:
                    transitions += 1
                else:
                    scenes += 1
        return scenes, transitions

    def burn_captions(self):
        cmd = [f'ruby', f'{BURN_CAPTIONS}',
               f'--input-file', f'{self.output_dir / UNCAPTIONED_FILE}',
               f'--srt-file', f'{self.output_dir / ASS_FILE}',
               f'--output_file', f'{self.video_file_path}']
        # TODO: raise error if failure
        # kaki
        self.run_cmd_and_log(cmd)

    # def make_scenes(self):
    #     for i, slide in enumerate(self.slides):
    #         cmd = [
    #             f'ruby', f'{SCENE_MAKER}', f'{slide.img_path}', f'{slide.scene_path}', f'--slide-duration={slide.scene_duration}',
    #             f'--zoom-rate=0.1', '--zoom-direction=random', f'--scale-mode={random.choice(SCALE_MODES)}', '-y']
    #
    #         slide.command = cmd
    #
    #         logger.info(f'ruby command {" ".join(cmd)}')
    #         result = subprocess.run(cmd, capture_output=True, text=True)
    #         if result.stderr:
    #             logger.warning(f"Failed to generate scene {slide}: -> {result.stdout} | {result.stderr}")
    #             slide.is_scene_created = False
    #         else:
    #             slide.is_scene_created = True
    #
    #     if sum(1 for slide in self.slides if slide.is_scene_created) < MINIMUM_SCENES:
    #         raise RuntimeError(f"Failed to create enough scenes, created: {sum(1 for slide in self.slides if slide.is_scene_created)}")
    #
    # def make_transitions(self):
    #     for i, slide in enumerate(self.slides[0:-1]):
    #         last_frame = self.extract_frame(slide, is_last=True)
    #         first_frame = self.extract_frame(self.slides[i+1], is_last=False)
    #         slide.transition_path = self.output_dir / SHARP_CUT_FILE_FORMAT.format(i, i + 1)
    #
    #         # This calculation is specifically for sharp cut, other transitions will have to be calculated differently
    #         slide.transition_duration = (FRAME_DURATION * SHARP_CUT_FRAME_DURATION)
    #         cmd = [f'ruby', f'{SHARP_CUT_MAKER}', f'{last_frame}', f'{first_frame}', f'{slide.transition_path}']
    #         slide.command = cmd
    #         self.run_cmd_and_log(cmd)

    @staticmethod
    def run_cmd_and_log(cmd, verbose=False) -> Tuple[bool, str]:
        message = ''

        logger.info(f'ruby command {" ".join(cmd)}')
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.stderr:
            message = f"Command failed: {result.stdout} | {result.stderr}"
            logger.warning(message)
            return False, message
        elif verbose:
            message = f"Command output: {result.stdout}"
            logger.info(message)
        return True, message

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

        narration_volume_adjustment = self._get_volume_adjustment(str(self.narration_file), is_narration=True)
        music_volume_adjustment = self._get_volume_adjustment(str(self.music_file), is_music=True)
        cmd = [f'ruby',
               f'{VIDEO_MAKER}',
               f'--file_list', f'{self.output_dir / FILE_LIST}',
               f'--durations', f'{",".join([str(_) for _ in durations])}',
               f'--background_music', f'{self.music_file}',
               f'--music-volume-adjustment', f'{music_volume_adjustment}',
               f'--narration-volume-adjustment', f'{narration_volume_adjustment}',
               f'--narration-audio', f'{self.narration_file}',
               f'--transition-sound-effect', f'{TRANSITION_SOUND_EFFECT}',
               f'--output_file', f'{self.output_dir / UNCAPTIONED_FILE}']

        result = self.run_cmd_and_log(cmd, verbose=True)
        if result[0] is False:
            raise RuntimeError(f"Failed to generate a video -> failure in connecting scenes: {result[1]}")

    def sharp_cut(self, images):
        images_string = " ".join(images)
        transition_file_path = os.path.join(self.output_dir, 'sharp_cut.mp4')
        cmd = [f'ruby', f'{SHARP_CUT_MAKER}', f'{images_string}', f'{transition_file_path}']

        self.run_cmd_and_log(cmd)

    def _generate_slides(self):
        # Generating slides with random durations
        # Each slide is an image

        video_duration = self._get_audio_duration(str(self.narration_file))
        scenes = os.listdir(self.output_dir / IMAGES_DIR)
        total_min_duration = MINIMUM_SCENE_DURATION * len(scenes)

        if (video_duration > MAX_VIDEO_DURATION) or (video_duration < total_min_duration):
            raise ValueError(f"Video duration doesn't match requirements: {MAX_VIDEO_DURATION} < {video_duration} > {total_min_duration}")

        remaining_duration = video_duration - total_min_duration

        # Randomly disparse scene durations
        extra_durations = [random.random() for _ in range(len(scenes))]
        normalized_extra_durations = [d / sum(extra_durations) * remaining_duration for d in extra_durations]
        durations = [MINIMUM_SCENE_DURATION + extra for extra in normalized_extra_durations]

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
    def _get_volume_adjustment(file_path: str, is_music=False, is_narration=False) -> float:
        # measure_loudness
        data, rate = sf.read(file_path)  # Read audio file

        meter = pyln.Meter(rate)  # create BS.1770 meter
        loudness = meter.integrated_loudness(data)  # measure loudness

        logger.info(f"kaki {'music' if is_music else 'narration'} {loudness}db")

        if is_music:
            gain = DEFAULT_MUSIC_GAIN - loudness
        elif is_narration:
            gain = DEFAULT_NARRATION_GAIN - loudness
        else:
            raise ValueError("One of is_music or is_narration should be True")
        return gain

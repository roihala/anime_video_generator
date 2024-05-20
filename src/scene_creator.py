import datetime
import logging
import os.path
import random
import subprocess
import threading
import time
import traceback
from concurrent.futures import ThreadPoolExecutor, Future, ProcessPoolExecutor
from pathlib import Path
from typing import List, Tuple, Dict

import cv2
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR, EVENT_JOB_ADDED, EVENT_JOB_REMOVED
from apscheduler.schedulers.base import STATE_RUNNING
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.date import DateTrigger
from pydantic import BaseModel

from config import logger, MAXIMUM_SCENES, FIRST_FRAME_PATH, SHARP_CUT_FILE_FORMAT, LAST_FRAME_PATH, SHARP_CUT_MAKER, \
    SCENE_MAKER, FRAME_DURATION, SHARP_CUT_FRAME_DURATION, SCALE_MODES
from src.pydantic_models.slide import Slide, SlideJob


SCENE_JOB_ID = 'scene-{}'
TRANSITION_JOB_ID = 'transition-{}'


class SceneCreator:
    def __init__(self, output_dir: Path, slides: List[Slide]):
        self.output_dir = output_dir
        self.slides = slides
        # Max scenes + their transitions
        self.executor = ThreadPoolExecutor(5)
        self.slide_jobs: Dict[str, SlideJob] = {}
        self.all_jobs_done_event = threading.Event()
        self.kaki_counter = 0

    def run(self) -> Dict[str, SlideJob]:
        # Forcing termination after 10 minutes
        monitor_thread = threading.Thread(target=self.monitor, args=(600,))
        monitor_thread.start()
        for slide in self.slides:
            job_id = self._generate_job_id(slide, False)

            self.slide_jobs[job_id] = SlideJob(
                slide=slide,
                job_id=job_id,
                is_transition=False,
                is_finish=False,
                is_success=False
            )

            # Not generating last transition
            if not slide == self.slides[-1]:
                transition_job_id = self._generate_job_id(slide, True)

                self.slide_jobs[transition_job_id] = SlideJob(
                    slide=slide,
                    job_id=transition_job_id,
                    is_transition=True,
                    is_finish=False,
                    is_success=False
                )

            future = self.executor.submit(self.scene_job, slide)
            future.__dict__['id'] = job_id
            future.add_done_callback(self.done_callback)
        self.all_jobs_done_event.wait()

        logging.info("Killing executor")
        self.executor.shutdown()

        return self.slide_jobs

    def run_cmd_and_log(self, cmd, slide, is_transition) -> bool:
        start_time = time.time()
        logger.info(f'ruby command {" ".join(cmd)}')

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.stderr:
            is_success = False
            logger.warning(f"Command failed: {result.stdout} | {result.stderr}")
        else:
            is_success = True
        end_time = time.time()

        slide_job = self.slide_jobs.get(self._generate_job_id(slide, is_transition=is_transition))
        if not slide_job:
            return is_success

        slide_job.is_finish = True
        slide_job.is_success = is_success

        logger.info(f"Finished job {slide.index} {slide_job.job_id if slide_job else ''} | {' '.join(cmd)[0:7]}... in {end_time - start_time} | is success? {is_success}")
        return is_success

    def done_callback(self, future: Future):
        self.kaki_counter += 1
        if not future.done():
            logger.warning(F"logic error! Review this logic, {future}, {future.result()}, {future.exception()}")
            return

        slide_job = self.slide_jobs[future.id]
        slide_job.is_finish = True

        try:
            slide_job.is_success = True

        except Exception as exc:
            slide_job.is_success = False
            logger.info(f'job failed with exception: {exc} -> {traceback.print_exc()}')

        if not slide_job.is_transition:
            self._schedule_transition(slide_job)

    def _schedule_transition(self, slide_job: SlideJob):
        # Not making a transition on last scene
        if slide_job.slide.index == self.slides[-1].index:
            return
        job_id = self._generate_job_id(slide_job.slide, True)

        future = self.executor.submit(self.transition_job, slide_job.slide)
        future.__dict__['id'] = job_id
        future.add_done_callback(self.done_callback)

    def scene_job(self, slide: Slide):
        try:
            cmd = [
                f'ruby', f'{SCENE_MAKER}', f'{slide.img_path}', f'{slide.scene_path}',
                f'--slide-duration={slide.scene_duration}',
                f'--zoom-rate=0.1', '--zoom-direction=random', f'--scale-mode={random.choice(SCALE_MODES)}', '-y']
            self.run_cmd_and_log(cmd, slide, False)
        except Exception as e:
            logger.warning(f"scene job failure: {e} -> {traceback.print_exc()}")

    def transition_job(self, slide: Slide):
        try:
            self._wait_for_next_slide(slide)

            last_frame = self.extract_frame(slide, is_last=True)
            first_frame = self.extract_frame(self.slides[slide.index + 1], is_last=False)
            slide.transition_path = self.output_dir / SHARP_CUT_FILE_FORMAT.format(slide.index, slide.index + 1)
            slide.transition_duration = (FRAME_DURATION * SHARP_CUT_FRAME_DURATION)
            cmd = [f'ruby', f'{SHARP_CUT_MAKER}', f'{last_frame}', f'{first_frame}', f'{slide.transition_path}']
            self.run_cmd_and_log(cmd, slide, True)
        except Exception as e:
            logger.warning(f"transition job failure: {e} -> {traceback.print_exc()}")

    def _wait_for_next_slide(self, current_slide):
        job_id = self._generate_job_id(self.slides[current_slide.index + 1], is_transition=False)
        # Waiting in order to extract the first frame of this slide for transitions
        # 120 * 3 seconds = 6 minutes
        for i in range(120):
            if self.slide_jobs[job_id].is_finish:
                return
            time.sleep(3)

        raise RuntimeError(f"Couldn't generate transition because next slide wasn't created: current_slide {current_slide}")

    def extract_frame(self, slide: Slide, is_last=True):
        # if not is_last - will extract first frame
        video_path = slide.scene_path
        # Capture the video
        cap = cv2.VideoCapture(str(video_path))
        # Check if video opened successfully
        if not cap.isOpened():
            logger.warning(f"Error opening video file: {video_path} | is_last? {is_last}")
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

        try:
            # Check if the frame was captured successfully
            if ret:
                # Save the frame as an image
                cv2.imwrite(str(image_path), frame)
                if is_last:
                    return image_path
                else:
                    return image_path
            else:
                logger.warning("Error extracting frame")
        finally:
            # Release the video capture object
            cap.release()
            cv2.destroyAllWindows()

    # Function to monitor and trigger the stop event
    def monitor(self, execution_time):

        for second in range(execution_time):
            # We're finished if all slides and transition -1 have finished running
            # -1 because last transition is skipped
            if len(self.slides) * 2 - 1 == sum([1 for sj in self.slide_jobs.values() if sj.is_finish]):
                break
            else:
                time.sleep(1)

        # Effectively shuts down
        self.all_jobs_done_event.set()

    def _generate_job_id(self, slide: Slide, is_transition):
        if not is_transition:
            return SCENE_JOB_ID.format(slide.index)
        else:
            return TRANSITION_JOB_ID.format(slide.index)

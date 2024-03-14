#
#  video_maker.py
#
#  Created by Eldar Eliav on 2023/05/13.
#
import os
import random
import cv2

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

# Default target loudness, in decibels
DEFAULT_TARGET_LOUDNESS = -8
SCALE_MODES = ['pad', 'pan']


# Frame duration per 60 fps = 1 / 60(frames) ≈ 16.67
FRAME_DURATION = 1 / 60
SHARP_CUT_FRAME_DURATION = 12
MAX_VIDEO_DURATION = 30

class Slide(BaseModel):
    index: int
    img_path: Path
    scene_path: Path
    scene_duration: float
    transition_path: Path = None
    transition_duration: float = None
    first_frame_path: Path = None
    last_frame_path: Path = None


class VideoMaker:
    def __init__(self, video_dir: Path, narration_file_path: Path):
        self.video_dir = video_dir
        self.output_dir: Path = video_dir / OUTPUT_DIR
        self.narration_file_path = narration_file_path
        self.slides = []
        self._generate_slides()

        # TODO
        video_file_path = video_dir / "video.mp4"
        self.video_file_path = video_file_path

    def make_video(self):
        self.make_scenes()
        self.make_transitions()
        # self.connect_all()

    def make_scenes(self):
        for i, slide in enumerate(self.slides):
            cmd = (
                f'ruby {SCENE_MAKER} {slide.img_path} {slide.scene_path} --slide-duration={slide.scene_duration} '
                f'--zoom-rate=0.1 --zoom-direction=random --scale-mode={random.choice(SCALE_MODES)} -y')

            log.info(f'ruby command {cmd}')
            os.system(cmd)

    def make_transitions(self):
        for i, slide in enumerate(self.slides[0:-1]):
            last_frame = self.extract_frame(slide, is_last=True)
            first_frame = self.extract_frame(self.slides[i+1], is_last=False)
            slide.transition_path = self.output_dir / SHARP_CUT_FILE_FORMAT.format(i, i + 1)

            # This calculation is specifically for sharp cut, other transitions will have to be calculated differently
            slide.transition_duration = (FRAME_DURATION * SHARP_CUT_FRAME_DURATION)
            cmd = f'ruby {SHARP_CUT_MAKER} {last_frame} {first_frame} {slide.transition_path}'
            log.info(f'ruby command {cmd}')
            os.system(cmd)
            log.info(f"video generated : {slide.transition_path}")

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

        background_music, volume_adjustment = self._get_background_audio(sum(durations))

        cmd = (f'ruby {VIDEO_MAKER} '
               f'--file_list {self.output_dir / FILE_LIST} '
               f'--durations "{','.join([str(_) for _ in durations])}" '
               f'--background_music "{background_music}" '
               f'--music-volume-adjustment {volume_adjustment} '
               f'--narration-audio "{self.narration_file_path}" '
               f'--transition-sound-effect "{TRANSITION_SOUND_EFFECT}" ' 
               f'--output_file "{self.video_file_path}"')

        log.info(f'ruby command {cmd}')
        os.system(cmd)
        log.info(f"video finished : {self.video_file_path}")

    def sharp_cut(self, images):
        images_string = " ".join(images)
        transition_file_path = os.path.join(self.video_dir, 'sharp_cut.mp4')
        cmd = f'ruby {SHARP_CUT_MAKER} {images_string} {transition_file_path}'

        log.info(f'ruby command {cmd}')
        os.system(cmd)
        log.info(f"video generated : {self.video_file_path}")

    def extract_frame(self, slide: Slide, is_last=True):
        # if not is_last - will extract first frame
        video_path = slide.scene_path
        # Capture the video
        cap = cv2.VideoCapture(str(video_path))
        # Check if video opened successfully
        if not cap.isOpened():
            log.warning("Error opening video file", None)
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
            log.warning("Error extracting the last frame", None)

        # Release the video capture object
        cap.release()
        cv2.destroyAllWindows()

    def _generate_slides(self):
        # Generating slides with random durations
        # Each slide is an image

        video_duration = self._get_audio_duration(str(self.narration_file_path))
        if video_duration > MAX_VIDEO_DURATION:
            raise ValueError(f"Video duration is too long - {self.narration_file_path}")

        scenes = os.listdir(self.video_dir / IMAGES_DIR)

        # Randomly disparse scene durations
        durations = [random.random() for _ in range(len(scenes))]
        durations = [d / sum(durations) * video_duration for d in durations]

        for i in range(len(scenes)):
            self.slides.append(
                Slide(index=i,
                      img_path=self.video_dir / IMAGES_DIR / scenes[i],
                      scene_duration=durations[i],
                      scene_path=self.output_dir / SCENE_FILE_FORMAT.format(index=i))
            )

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

#
#  video_maker.py
#
#  Created by Eldar Eliav on 2023/05/13.
#
import os

from log import log
from pydub import AudioSegment


OUTPUT_FILE_NAME = "video.mp4"
MAKER_SCRIPT = 'maker.rb'
TOOLS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tools')


class VideoMaker:
    def make_video(
        self,
        video_dir: str,
        voice_file_path: str,
    ):
        log.info("generating video...")

        file_destination = os.path.join(video_dir, 'video', OUTPUT_FILE_NAME)
        images_dir = os.path.join(video_dir, 'images')
        images_list = [os.path.join(images_dir, f) for f in os.listdir(images_dir) if os.path.isfile(os.path.join(images_dir, f))]

        slide_duration = self._calculate_slide_daration(
            audio_duration= self._get_audio_duration(voice_file_path),
            number_of_images = len(images_list)
        )

        images_string = " ".join(images_list)

        cmd = f'ruby {os.path.join(TOOLS_DIR, MAKER_SCRIPT)} {images_string} {file_destination} --size=1080x1920 --slide-duration={slide_duration} --fade-duration=1 --zoom-rate=0.2 --zoom-direction=random --scale-mode=pad --fps=120 --audio={voice_file_path} -y'
        os.system(cmd)

        # TODO: how to tell if it was successful?
        log.info(f"video generated : {file_destination}")

    # private methods
    def _calculate_slide_daration(self, audio_duration: int, number_of_images: int) -> float:
        return audio_duration / number_of_images

    def _get_audio_duration(self, mp3_audio_file_path: str) -> int:
        audio_object = AudioSegment.from_file(mp3_audio_file_path, format="mp3")
        return audio_object.duration_seconds

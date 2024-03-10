#
#  captions_generator.py
#
#  Created by Eldar Eliav on 2023/05/13.
#
import os
from typing import Iterator, TextIO

import whisper
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
from moviepy.video.tools.subtitles import SubtitlesClip


class CaptionsGenerator:
    def __init__(self, voice_file_path, srt_file_path):
        self.voice_file_path = voice_file_path
        self.srt_file_path = srt_file_path

    # api memthods
    def generate_captions(self) -> bool:
        model = whisper.load_model('base')
        transcription = model.transcribe(self.voice_file_path)

        with open(self.srt_file_path, "w", encoding="utf-8") as srt:
            self.write_srt(transcription["segments"], file=srt)

    @classmethod
    def write_srt(cls, transcript: Iterator[dict], file: TextIO):
        for i, segment in enumerate(transcript, start=1):
            print(
                f"{i}\n"
                f"{cls.format_timestamp(segment['start'], always_include_hours=True)} --> "
                f"{cls.format_timestamp(segment['end'], always_include_hours=True)}\n"
                f"{segment['text'].strip().replace('-->', '->')}\n",
                file=file,
                flush=True,
            )

    @classmethod
    def format_timestamp(cls, seconds: float, always_include_hours: bool = False):
        assert seconds >= 0, "non-negative timestamp expected"
        milliseconds = round(seconds * 1000.0)

        hours = milliseconds // 3_600_000
        milliseconds -= hours * 3_600_000

        minutes = milliseconds // 60_000
        milliseconds -= minutes * 60_000

        seconds = milliseconds // 1_000
        milliseconds -= seconds * 1_000

        hours_marker = f"{hours:02d}:" if always_include_hours or hours > 0 else ""
        return f"{hours_marker}{minutes:02d}:{seconds:02d},{milliseconds:03d}"

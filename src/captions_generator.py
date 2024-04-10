#
#  captions_generator.py
#
#  Created by Eldar Eliav on 2023/05/13.
#
import os
from pathlib import Path
from typing import TextIO, Iterator

import assemblyai as aai
import whisper

# Replace with your API key
aai.settings.api_key = "46bc81326eaf4d07977b48a652df2731"

# URL of the file to transcribe
FILE_URL = "https://imxze2im7tagxmrw.public.blob.vercel-storage.com/video-TbkjQolF9Oysyc0VMpNqeMUGVyyqeI.mp4"
DEMO_DIR = Path(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'demo_output'))

# You can also transcribe a local file by passing in a file path
# FILE_URL = './path/to/file.mp3'

transcriber = aai.Transcriber()
transcript = transcriber.transcribe(FILE_URL)

if transcript.status == aai.TranscriptStatus.error:
    print(transcript.error)
else:
    print(transcript.text)

with open(DEMO_DIR/'tmp.srt', 'w') as file:
    file.write(transcript.export_subtitles_srt())
with open(DEMO_DIR / 'words.txt', 'w') as file:
    file.write('\n'.join([str(_) for _ in transcript.words]))

import re

def parse_line(line):
    match = re.match(r"text='(.+?)'\sstart=(\d+)\send=(\d+)", line)
    if match:
        return match.groups()
    return None

def format_time(milliseconds):
    """Convert milliseconds to SRT timestamp format."""
    hours = milliseconds // 3600000
    milliseconds %= 3600000
    minutes = milliseconds // 60000
    milliseconds %= 60000
    seconds = milliseconds // 1000
    milliseconds %= 1000
    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"

def generate_srt(lines):
    srt_entries = []
    buffer = []
    for line in lines:
        parsed = parse_line(line)
        if parsed:
            buffer.append(parsed)
            if len(buffer) == 3:
                # Process buffer
                start_times = [int(word[1]) for word in buffer]
                end_times = [int(word[2]) for word in buffer]
                grouped_text = " ".join([word[0] for word in buffer])
                # Generate SRT entry for the whole group
                srt_entry = f"{format_time(min(start_times))} --> {format_time(max(end_times))}\n{grouped_text}\n"
                srt_entries.append(srt_entry)
                buffer = []
    return srt_entries
#
# # Read the words file
# with open("words_file.txt", "r") as file:
#     lines = file.readlines()
#
# srt_entries = generate_srt(lines)
#
# # Write to SRT file
# with open("output.srt", "w") as file:
#     for i, entry in enumerate(srt_entries, 1):
#         file.write(f"{i}\n{entry}\n")
#
# print("SRT file generated successfully.")
#



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

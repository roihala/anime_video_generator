#!/usr/bin/env python3
#
#  main.py
#
#  Created by Eldar Eliav on 2023/05/11.
#

from os import path, makedirs
from log import log
from script_generator import ScriptGenerator
from script_narration import ScriptNarration
from captions_generator import CaptionsGenerator
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip

from video_maker import VideoMaker
from dotenv import load_dotenv
import os

load_dotenv()  # This loads the variables from '.env' into the environment

DEBUG = os.getenv('DEBUG') == 'True'

DESTINATION_DIR = "./demo_output/"
VOICE_NAME = 'Adam'
VOICE_FILE = "awesome_voice.mp3"
VIDEO_DIR_STRUCTURE = ['images', 'video']


def generate_video(voice_name: str, video_dir: str):
    # Prepare
    if not path.exists(video_dir):
        os.makedirs(os.path.join(video_dir), exist_ok=True)

    # Create each subdirectory
    for subdir in VIDEO_DIR_STRUCTURE:
        os.makedirs(os.path.join(video_dir, subdir), exist_ok=True)

    if os.getenv('DEBUG'):
        video = VideoFileClip(r"C:\Users\RoiHa\PycharmProjects\anime_video_generator\temp\video.mp4")
        caption = TextClip("Your Caption Here", fontsize=24, color='white', font="Arial")
        caption = caption.set_pos('bottom').set_duration(10)
        final_video = CompositeVideoClip([video, caption.set_start(3)])  # Caption starts at 3 seconds
        # final_video.write_videofile(r"C:\Users\RoiHa\PycharmProjects\anime_video_generator\temp\video_captionated.mp4")
        import speech_recognition as sr

        # Load your audio file
        r = sr.Recognizer()
        with sr.AudioFile(r'C:\Users\RoiHa\PycharmProjects\anime_video_generator\temp\temp_audio.mp3') as source:
            audio = r.record(source)

        # Try recognizing the audio (using Google's Web API in this example)
        try:
            transcription = r.recognize_google(audio)
            print(transcription)
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")

        return
    log.info("STEP 0 - Prepare images")
    # TODO: image getter
    # images_path_list = [r"C:\Users\RoiHa\PycharmProjects\anime_video_generator\demo_output\007.jpg", r"C:\Users\RoiHa\PycharmProjects\anime_video_generator\demo_output\011.jpg", r"C:\Users\RoiHa\PycharmProjects\anime_video_generator\demo_output\018.jpg", r"C:\Users\RoiHa\PycharmProjects\anime_video_generator\demo_output\028.jpg"]


    log.info("STEP 1 - script")
    script = ScriptGenerator().generate()

    log.info("STEP 2 - narration")
    voice_file_path = path.join(video_dir, VOICE_FILE)
    ScriptNarration().narrate(voice_name, script, voice_file_path)

    # log.info("STEP 3 - captions")
    # generated_images_path_list = CaptionsGenerator().generate_captions(
    #     captions_string = captions,
    #     destination_dir = destination_dir,
    #     is_crop_to_ratio_16_9 = True
    # )

    log.info("STEP 4 - video")
    VideoMaker().make_video(video_dir, voice_file_path)


if __name__ == "__main__":
    generate_video(
        voice_name = VOICE_NAME,
        video_dir= DESTINATION_DIR
    )

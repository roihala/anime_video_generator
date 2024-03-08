#
#  captions_generator.py
#
#  Created by Eldar Eliav on 2023/05/13.
#

from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
import speech_recognition as sr


class CaptionsGenerator:
    # api memthods
    def generate_captions(self) -> bool:
        # returns a list of paths to the generated images
        video = VideoFileClip(r"C:\Users\RoiHa\PycharmProjects\anime_video_generator\temp\video.mp4")
        caption = TextClip("Your Caption Here", fontsize=24, color='white', font="Arial")
        caption = caption.set_pos('bottom').set_duration(10)
        final_video = CompositeVideoClip([video, caption.set_start(3)])  # Caption starts at 3 seconds
        # final_video.write_videofile(r"C:\Users\RoiHa\PycharmProjects\anime_video_generator\temp\video_captionated.mp4")

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

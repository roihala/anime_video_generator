#
#  script_narration.py
#
#  Created by Eldar Eliav on 2023/05/11.
#
import os
import random
from io import BytesIO
from pydub import AudioSegment
from eleven_labs_voice_generation import ElevenLabsVoiceGeneration

class ScriptNarration:
    # init
    def __init__(self):
        pass

    # api methods
    def narrate(
        self,
        voice_name: str,
        full_script: str,
        mp3_file_destination_with_extension: str
    ):
        voice_generator = ElevenLabsVoiceGeneration()
        paragraphs = full_script.split('\n\n')
        total_audio = AudioSegment.silent(duration=500)
        for paragraph in paragraphs:
            random_silence = random.randint(1000, 2000)
            audio_bytes = voice_generator.generate_audio(voice_name, paragraph)
            audio_object = self._convert_audio_bytes_to_audio_object(audio_bytes)
            total_audio += audio_object + AudioSegment.silent(duration=random_silence)
            # TODO - randomly add audio between paragraphs: "hmmm", "ahhh", "so..." (premade to save money?)
        total_audio.export(mp3_file_destination_with_extension, format = "mp3")

    # private methods
    def _convert_audio_bytes_to_audio_object(self, audio_bytes: bytes):
        # # Define the path where you want to save the audio file
        # file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'temp', 'temp_audio.mp3')
        #
        # # Open the file in binary write mode and write the audio bytes to it
        # with open(file_path, 'wb') as audio_file:
        #     audio_file.write(audio_bytes)
        #     return AudioSegment.from_file(audio_file)
        audio_file = BytesIO(audio_bytes)
        return AudioSegment.from_file(audio_file)

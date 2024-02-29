#
#  eleven_labs_voice_generation.py
#
#  Created by Eldar Eliav on 2023/05/11.
#

from elevenlabs import get_api_key, generate, voices, save, set_api_key


class ElevenLabsVoiceGeneration:
    class MissingAPIKey(Exception):
        pass

    def __init__(self):
        # TODO: api key
        set_api_key('3e3b2d2de8a783682b8d7e65311daf6e')
        if get_api_key() is None:
            raise self.MissingAPIKey()
        voices()  # load all available voice from remote, incliding private generated onces

    def generate_audio(self, voice_name: str, text: str) -> bytes:
        return generate(
            text = text,
            voice = voice_name,
            model = "eleven_monolingual_v1"
        )

    def generate_audio_and_save(self, voice_name: str, text: str, mp3_file_destination_with_extension: str):
        audio = self.generate_audio(voice_name, text)
        save(audio, mp3_file_destination_with_extension)

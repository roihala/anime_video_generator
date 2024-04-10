#
#  narrator.py
#
#  Created by Eldar Eliav on 2023/05/11.
#
import json
import os
from src.log import log
from io import BytesIO
from pathlib import Path

import requests
from pydub import AudioSegment


class Narrator:
    def __init__(self):
        self.play_ht_userid = os.getenv("PLAY_HT_USER_ID")
        self.play_ht_api_key = os.getenv("PLAY_HT_API_KEY")
        self.narration_response = None

    def narrate(self, voice_url: str, script: str) -> str:
        """
        https://docs.play.ht/reference/api-generate-audio
        """
        url = "https://api.play.ht/api/v2/tts"

        voice_url = "s3://voice-cloning-zero-shot/d9ff78ba-d016-47f6-b0ef-dd630f59414e/female-cs/manifest.json"

        payload = {
            "text": script,
            "voice": voice_url,
            "output_format": "mp3",
            "voice_engine": "PlayHT2.0"
        }
        headers = {
            "accept": "text/event-stream",
            "content-type": "application/json",
            "AUTHORIZATION": self.play_ht_api_key,
            "X-USER-ID": self.play_ht_userid
        }

        response = requests.post(url, json=payload, headers=headers)
        self.narration_response = self.parse_playht_response(response.text)
        return self.narration_response.get('url')

    def request_transcription(self):
        """
        https://docs.play.ht/reference/api-transcribe-audio
        """
        if self.narration_response is None:
            raise RuntimeError("Can't request transcription before narration")
        url = "https://api.play.ht/api/v2/transcriptions"

        payload = {
            "format": "SRT",
            "timestamp_level": "WORD",
            "tts_job_id": self.narration_response.get('id'),
            # todo: webhook
            "webhook_url": "https://webhook.site/f3fcb54c-24ce-47e6-9a65-663770829de1"
        }
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "AUTHORIZATION": self.play_ht_api_key,
            "X-USER-ID": self.play_ht_userid
        }

        # Send and hope for good
        response = requests.post(url, json=payload, headers=headers)
        if not response.status_code == 201:
            raise ConnectionError("Couldn't setup srt file webhook")

    # api methods
    def parse_playht_response(self, response_text) -> dict:
        try:
            # Matching play.ht format:
            # Getting last response
            last_response = response_text.strip('\r\n\r\n').split('\r\n\r\n')[-1]

            # Getting event status:
            if last_response.split('\r\n')[0].strip('event: ') == 'completed':
                return json.loads(last_response.split('\r\n')[-1].lstrip('data: '))
        except Exception as e:
            log.error(f"Couldn't parse playht response: {response_text}", e)

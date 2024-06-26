#
#  narrator.py
#
#  Created by Eldar Eliav on 2023/05/11.
#
import json
import os
import time
import traceback

import requests

from config import logger


class Narrator:
    def __init__(self):
        self.play_ht_userid = os.getenv("PLAY_HT_USER_ID")
        self.play_ht_api_key = os.getenv("PLAY_HT_API_KEY")
        self.narration_response = None

    def narrate(self, voice: str, script: str) -> (str, str):
        """
        https://docs.play.ht/reference/api-generate-audio
        """
        url = "https://api.play.ht/api/v2/tts"

        # TODO: default voice?
        voice = voice if voice else "s3://voice-cloning-zero-shot/820da3d2-3a3b-42e7-844d-e68db835a206/sarah/manifest.json"
        payload = {
            "text": script,
            "voice": voice,
            "output_format": "mp3",
            "voice_engine": "PlayHT2.0"
        }
        headers = {
            "accept": "text/event-stream",
            "content-type": "application/json",
            "AUTHORIZATION": self.play_ht_api_key,
            "X-USER-ID": self.play_ht_userid
        }
        response = ''
        for attempt in range(5):
            try:
                response = requests.post(url, json=payload, headers=headers)
                self.narration_response = self.parse_playht_response(response.text)
                if self.narration_response:
                    break
                time.sleep(0.2)
            except Exception as e:
                logger.warning(f"Couldn't get narration response: {response.text} {e}")
                continue
        if not self.narration_response:
            raise RuntimeError(f"Couldn't connect to narration API: {response.text}")

        return self.narration_response.get('id'), self.narration_response.get('url')

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
            "webhook_url": os.getenv("TRANSCRIPTION_WEBHOOK_URL")
        }
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "AUTHORIZATION": self.play_ht_api_key,
            "X-USER-ID": self.play_ht_userid
        }
        response = None

        for _ in range(20):
            # Send and hope for good
            response = requests.post(url, json=payload, headers=headers)

            try:
                if response.status_code == 201:
                    return
                elif 'is not complete. Please wait a few moments and try again.' in response.json().get('error_message'):
                    continue
                else:
                    logger.info(f'Couldnt setup srt file webhook, {_} tries')
            except Exception as e:
                logger.error(f"Error while trying to parse response, failing: {str(e)} -> {traceback.print_exc()}")
            finally:
                time.sleep(3)
        raise ConnectionError(f"Failed to request transcription file, {response if response else ''}:{response.content if response else ''}")

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
            logger.error(f"Couldn't parse playht response: {response_text}: {str(e)} -> {traceback.print_exc()}")

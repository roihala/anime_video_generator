import json
import random

import pytest
import requests

from config import VOICES_JSON, logger

toontube_stories = [
        'https://toontube.co/reader/6400809b651f9fc369319f43/653672907b605c94f734f89a?page={}',
        'https://toontube.co/reader/643e7e64318330950c33f4e3/643e83f2318330950c33f4e5?page={}',
        'https://toontube.co/reader/6429646b02cbbf0de9fd236e/64ddd30190bcd1c401311df8?page={}',
        'https://toontube.co/reader/641e0cc005708b29765e697a/64ddc6b1a6b3a801190a7bca?page={}'
        'https://toontube.co/reader/64d63d7b9c2e412464643d30/64d643592f2dac342317c413?page={}'
        'https://toontube.co/reader/6429646b02cbbf0de9fd236e/64ddd30190bcd1c401311df8?page={}'
        'https://toontube.co/reader/64d60ebb9c2e4124646429e9/64d60f302f2dac342317a727?page={}'
     ]

def test_app():

    headers = {"Content-Type": "application/json"}
    payload = {'prompt': 'alien comics',
               'callback_url': r'https://webhook.site/e7eb4ce4-77bf-4961-9fc5-64c9ad3b0ae9',
               'voice': get_random_voice()}
    # payload['story_images'] = list(pages)[0:5]

@pytest.mark.latest
def test_toontube():
    headers = {"Content-Type": "application/json"}
    payload = {
        'prompt': 'alien comics',
        'callback_url': r'https://webhook.site/03ad89e5-c33c-4437-b2a0-0f8ea0ec383e'}
    for story in toontube_stories:
        try:
            payload['voice'] = get_random_voice()
            payload['story_images'] = [story]
            logger.info(f"Posting with payload: {payload}")
            requests.post('http://104.155.194.43/story_to_video', json=payload, headers=headers)

        except Exception as e:
            logger.warning(f"Couldn't fetch story: {story}")
            logger.error(e)
        # kaki
        break

def get_random_voice():
    with open(VOICES_JSON, 'r') as f:
        voices = json.loads(f.read())
    return random.choice(voices)['id']

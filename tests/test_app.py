import json
import random
import time

import pytest
import requests

from config import VOICES_JSON, logger

toontube_stories = [
        'https://toontube.co/reader/6400809b651f9fc369319f43/653672907b605c94f734f89a?page=1',
        'https://toontube.co/reader/643e7e64318330950c33f4e3/643e83f2318330950c33f4e5?page=1',
        'https://toontube.co/reader/6429646b02cbbf0de9fd236e/64ddd30190bcd1c401311df8?page=1',
        'https://toontube.co/reader/641e0cc005708b29765e697a/64ddc6b1a6b3a801190a7bca?page=1',
        'https://toontube.co/reader/6429646b02cbbf0de9fd236e/64ddd30190bcd1c401311df8?page=1',
        'https://toontube.co/reader/6429646b02cbbf0de9fd236e/64ddd30190bcd1c401311df8?page=1',
        'https://toontube.co/reader/641e0cc005708b29765e697a/64ddc6b1a6b3a801190a7bca?page=1',
        'https://toontube.co/reader/648ac3b80e6df15094ec1ee1/64918f6c966f84c8e5e42332?page=1',
        'https://toontube.co/reader/6537962a35f2b00dc92199c7/6537968835f2b00dc92199e2?page=1',
        'https://toontube.co/reader/65c4d8575b61996b390efb0b/65c6612b6463020a82fad303?page=1',
        'https://toontube.co/reader/66326fa0d960ccba09a67dcc/66327005d960ccba09a67de0?page=1',
        'https://toontube.co/reader/6429646b02cbbf0de9fd236e/64ddd30190bcd1c401311df8?page=1'
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
    test_local = False
    for story in toontube_stories:
        try:
            payload['voice'] = get_random_voice()
            payload['story_images'] = [story]
            payload['is_toontube'] = True
            logger.info(f"Posting with payload: {payload}")
            if test_local:
                requests.post('http://localhost:8000/story_to_video', json=payload, headers=headers)
            else:
                requests.post('http://34.81.214.9/story_to_video', json=payload, headers=headers)

        except Exception as e:
            logger.warning(f"Couldn't fetch story: {story}")
            logger.error(e)
        time.sleep(180)


def get_random_voice():
    with open(VOICES_JSON, 'r') as f:
        voices = json.loads(f.read())
    return random.choice(voices)['id']

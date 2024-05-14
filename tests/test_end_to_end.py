import asyncio
import time

import pytest

from app import process_story_to_video
from src.story_to_video_request import StoryToVideoRequest



def test_end_to_end():
    print('kaki')
    request_payload = {
        'story_images': [
            "https://storage.googleapis.com/public_stories/abc/007.jpg",
            "https://storage.googleapis.com/public_stories/abc/011.jpg",
            "https://storage.googleapis.com/public_stories/abc/018.jpg",
            "https://storage.googleapis.com/public_stories/abc/028.jpg"
        ],
        'prompt': 'A comic book about aliens from mars',
        'callback_url': 'https://webhook.site/00047bb5-2f06-4b71-8fae-13730d0b630f',
        'voice': 'adam'
    }

    request = StoryToVideoRequest(**request_payload)
    asyncio.run(process_story_to_video(request))
    assert True
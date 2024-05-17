import asyncio
import time
from pathlib import Path
from unittest.mock import Mock
from requests.models import Response

import pytest

from app import process_story_to_video
from src.manager import Manager
from src.pydantic_models.story_to_video_request import StoryToVideoRequest
from src.video_maker import VideoMaker
from tests.test_app import toontube_stories, get_random_voice


@pytest.fixture
def mock_request():
    # Create a mock response object
    mock_model = Mock(spec=StoryToVideoRequest)
    mock_model.story_images = toontube_stories[0]
    mock_model.prompt = 'A comic book about aliens from mars'
    mock_model.callback_url = 'https://webhook.site/00047bb5-2f06-4b71-8fae-13730d0b630f'
    mock_model.voice = get_random_voice()
    mock_model.is_toontube = True
    return mock_model

def test_end_to_end(mock_request):
    x = asyncio.run(process_story_to_video(mock_request))
    print(x)
    assert True

def test_video_maker(mock_request):
    story_id = 'tVpqQmQXkzuJqA1wRM'
    output_dir = Path(r'/Users/roihala/PycharmProjects/anime_video_generator/output')
    music_file = Manager(output_dir).fetch_random_music()
    videomaker = VideoMaker(story_id, output_dir / story_id, music_file).make_video()


import asyncio
import time
from pathlib import Path
from unittest.mock import Mock
from requests.models import Response

import pytest

from config import logger
from executor import Executor
from src.scene_creator import SceneCreator
from src.manager import Manager
from src.pydantic_models.story_to_video_request import StoryToVideoRequest
from src.video_maker import VideoMaker
from tests.test_app import toontube_stories, get_random_voice
from tests.test_ruby import slides


def mock_request():
    # Create a mock response object
    # mock_model = Mock(spec=StoryToVideoRequest)
    mock_model = StoryToVideoRequest(
        story_images=[toontube_stories[3]],
        prompt='A comic book about aliens from mars',
        callback_url='https://webhook.site/00047bb5-2f06-4b71-8fae-13730d0b630f',
        voice=get_random_voice(),
        is_toontube=True
    )
    return mock_model

def test_end_to_end():
    request = mock_request()
    Executor().story_to_video(request)
    assert True

@pytest.mark.latest
def test_video_maker():
    story_id = 'tVpqQmQXkzuJqA1wRM'
    output_dir = Path(r'/Users/roihala/PycharmProjects/anime_video_generator/output')
    music_file = Manager(output_dir).fetch_random_music()
    videomaker = VideoMaker(story_id, output_dir / story_id, music_file)
    videomaker.connect_all()
    assert True
    # videomaker.burn_captions()

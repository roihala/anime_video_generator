import subprocess
from pathlib import Path
import pytest

from config import VIDEO_MAKER, FILE_LIST, TRANSITION_SOUND_EFFECT, UNCAPTIONED_FILE, TOONTUBE_LOGO
from src.video_maker import VideoMaker
from src.pydantic_models.slide import Slide

slides = [
    Slide(
        index=0,
        img_path=Path('/Users/roihala/PycharmProjects/anime_video_generator/output/45KmQwtF5qecbixQNe/images/0.jpeg'),
        scene_path=Path('/Users/roihala/PycharmProjects/anime_video_generator/output/45KmQwtF5qecbixQNe/scene0.mp4'),
        scene_duration=5.5109742118471825,
        transition_path=Path(
            '/Users/roihala/PycharmProjects/anime_video_generator/output/45KmQwtF5qecbixQNe/sharpcut_0_1.mp4'),
        transition_duration=0.2
    ),
    Slide(
        index=1,
        img_path=Path('/Users/roihala/PycharmProjects/anime_video_generator/output/45KmQwtF5qecbixQNe/images/1.jpeg'),
        scene_path=Path('/Users/roihala/PycharmProjects/anime_video_generator/output/45KmQwtF5qecbixQNe/scene1.mp4'),
        scene_duration=6.003754739464292,
        transition_path=Path(
            '/Users/roihala/PycharmProjects/anime_video_generator/output/45KmQwtF5qecbixQNe/sharpcut_1_2.mp4'),
        transition_duration=0.2
    ),
    Slide(
        index=2,
        img_path=Path('/Users/roihala/PycharmProjects/anime_video_generator/output/45KmQwtF5qecbixQNe/images/2.jpeg'),
        scene_path=Path('/Users/roihala/PycharmProjects/anime_video_generator/output/45KmQwtF5qecbixQNe/scene2.mp4'),
        scene_duration=6.020906276993387,
        transition_path=Path(
            '/Users/roihala/PycharmProjects/anime_video_generator/output/45KmQwtF5qecbixQNe/sharpcut_2_3.mp4'),
        transition_duration=0.2
    ),
    Slide(
        index=3,
        img_path=Path('/Users/roihala/PycharmProjects/anime_video_generator/output/45KmQwtF5qecbixQNe/images/3.jpeg'),
        scene_path=Path('/Users/roihala/PycharmProjects/anime_video_generator/output/45KmQwtF5qecbixQNe/scene3.mp4'),
        scene_duration=6.133698105028472
    ),
    Slide(index=4,
          scene_path=TOONTUBE_LOGO,
          scene_duration=2.0)
]


def test_make_video():
    story_id = '45KmQwtF5qecbixQNe'
    music_file = Path(
        '/Users/roihala/PycharmProjects/anime_video_generator/output/AySMw7CQANDh5kIVX4/awesome_music.wav')
    videomaker = VideoMaker(story_id, Path(r'/Users/roihala/PycharmProjects/anime_video_generator/output') / story_id,
                            music_file, slides)
    videomaker.connect_all()
    assert True

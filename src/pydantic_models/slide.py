from pathlib import Path
from typing import List

from openai import BaseModel


class Slide(BaseModel):
    index: int
    scene_path: Path
    scene_duration: float
    command: List[str] = False
    transition_command: List[str] = False
    is_scene_created: bool = False
    img_path: Path = None
    transition_path: Path = None
    transition_duration: float = None


class SlideJob(BaseModel):
    # Describing a job of either a slide or a transition
    slide: Slide
    job_id: str
    is_transition: bool
    is_finish: bool
    is_success: bool

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, Query, Depends
from pydantic import BaseModel, HttpUrl, Field
from enum import Enum

from config import DEMO_DIR, VIDEO_DIR_STRUCTURE
from src.log import log
from src.narrator import Narrator
from src.script_generator import ScriptGenerator


load_dotenv()  # This loads the variables from '.env' into the environment
app = FastAPI()


class VoiceOption(str, Enum):
    male = "male"
    female = "female"
    custom = "custom"


class StoryToVideoRequest(BaseModel):
    story_url: HttpUrl = Query(..., description="The URL of the story to be converted to video")
    webhook_url: Optional[HttpUrl] = Field(None, description="The webhook URL to notify when processing is done")
    voice: Optional[VoiceOption] = Field(None, description="The voice to be used for narration")


@app.get("/story_to_video")
async def read_items(request: StoryToVideoRequest = Depends()):
    """
    This function expects a story URL and a webhook URL to notify when it's done.
    """
    video_dir = Path(DEMO_DIR)
    # Prepare
    if not os.path.exists(video_dir):
        os.makedirs(os.path.join(video_dir), exist_ok=True)

    # Create each subdirectory
    for subdir in VIDEO_DIR_STRUCTURE:
        os.makedirs(os.path.join(video_dir, subdir), exist_ok=True)

    log.info("STEP 0 - Prepare images")

    log.info("STEP 1 - script")
    script = ScriptGenerator().generate()

    log.info("STEP 2 - narration")

    narrator = Narrator()
    # TODO: voice from our api
    # narration_url = narrator.narrate(voice_name, script)
    narrator.request_transcription()

    # log.info("STEP 3 - video")
    # VideoMaker(video_dir, narration_url).make_video()
    return {"message": "Success", "story_url": request.story_url, "webhook_url": request.webhook_url, "voice": request.voice}


@app.get("/")
async def read_items():
    """
    This function expects for a story url and a webhook url to notify when it's done
    """
    return {"hello": "world"}

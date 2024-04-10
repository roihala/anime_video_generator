from typing import Optional

from fastapi import FastAPI, Query, Depends
from pydantic import BaseModel, HttpUrl, Field
from enum import Enum

app = FastAPI()


class VoiceOption(str, Enum):
    male = "male"
    female = "female"
    custom = "custom"
    empty = ''


class StoryToVideoRequest(BaseModel):
    story_url: HttpUrl = Query(..., description="The URL of the story to be converted to video")
    webhook_url: Optional[HttpUrl] = Field('', description="The webhook URL to notify when processing is done")
    voice: Optional[VoiceOption] = Field('', description="The voice to be used for narration")

@app.get("/story_to_video")
async def read_items(request: StoryToVideoRequest = Depends()):
    """
    This function expects a story URL and a webhook URL to notify when it's done.
    """
    return {"message": "Success", "story_url": request.story_url, "webhook_url": request.webhook_url, "voice": request.voice}


@app.get("/")
async def read_items():
    """
    This function expects for a story url and a webhook url to notify when it's done
    """
    return {"hello": "world"}

from openai import BaseModel
from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, Dict, Any, List
from fastapi import Query


class StoryToVideoRequest(BaseModel):
    story_images: List[HttpUrl] = Query(..., description="An ORDERED list of image URLs")
    prompt: str = Field(None, description="Story prompt for ChatGPT")
    callback_url: Optional[HttpUrl] = Field(None, description="The callback URL to notify when processing is done")
    voice: Optional[str] = Field(None, description="The voice to be used for narration")

from pydantic import BaseModel, Field

from src.pydantic_models.story_to_video_request import StoryToVideoRequest
from google.cloud.pubsub_v1.subscriber.message import Message as PubSubMessage


class ApiMessage(BaseModel):
    sub_url: str = Field(None, description="API suburl")
    request: StoryToVideoRequest = Field(None, description="Requst content")

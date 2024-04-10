import os
from pathlib import Path
from typing import Optional, Dict, Any

from dotenv import load_dotenv
from fastapi import FastAPI, Query, Depends, Request, HTTPException
from pydantic import BaseModel, HttpUrl, Field
from enum import Enum

from src.video_maker import VideoMaker

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


class TranscriptionData(BaseModel):
    job_id: str
    input: Dict[str, Any]
    results: Dict[str, Any]
    transcription: Optional[str] = None


@app.get("/story_to_video")
async def read_items(request: StoryToVideoRequest = Depends()):
    """
    This function expects a story URL and a webhook URL to notify when it's done.
    """
    VideoMaker().make_video()

    return {"message": "Success", "story_url": request.story_url, "webhook_url": request.webhook_url,
            "voice": request.voice}


@app.get("/transcription_webhook")
async def transcription_webhook(request: Request):
    body = await request.json()
    # Validate that the data structure matches what we expect
    try:
        data = TranscriptionData(**body["data"])
    except KeyError:
        # If the data does not have the expected structure, return a 400 error.
        raise HTTPException(status_code=400, detail="Invalid data structure")
    except Exception as e:
        # For any other exceptions, return a 500 server error.
        raise HTTPException(status_code=500, detail=str(e))

    # Check if the "transcription" part exists and process it accordingly
    if data.transcription:
        # Process the transcription part here
        print("Transcription:", data.transcription)
        # Respond that the request was processed successfully
        return {"message": "Transcription processed successfully."}
    else:
        # If there is no transcription, you might want to return a different message
        return {"message": "No transcription to process."}


@app.get("/")
async def read_items():
    """
    This function expects for a story url and a webhook url to notify when it's done
    """

    return {"hello": "world"}

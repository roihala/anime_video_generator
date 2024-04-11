from google.cloud import storage
import json
import os
import orjson
from pathlib import Path
from typing import Optional, Dict, Any, List

from dotenv import load_dotenv
from fastapi import FastAPI, Query, Depends, Request, HTTPException
from pydantic import BaseModel, HttpUrl, Field
from enum import Enum

from config import SRT_FILE
from src.log import log
from src.manager import Manager
from src.video_maker import VideoMaker

load_dotenv()  # This loads the variables from '.env' into the environment
app = FastAPI()


class VoiceOption(str, Enum):
    male = "male"
    female = "female"
    custom = "custom"


class StoryToVideoRequest(BaseModel):
    story_images: List[HttpUrl] = Query(..., description="An ORDERED list of image URLs")
    script: str = Field(None, description="The script of the story")
    webhook_url: Optional[HttpUrl] = Field(None, description="The webhook URL to notify when processing is done")
    voice: Optional[VoiceOption] = Field(None, description="The voice to be used for narration")


@app.post("/story_to_video")  # Note the change to @app.post()
async def story_to_video(request: StoryToVideoRequest):  # The request parameter is now a Pydantic model, indicating a JSON body
    """
    This function expects a JSON body with a story URL, an optional webhook URL, and an optional voice option to notify when it's done.
    """
    try:
        Manager().manage(request.story_images)
        return {"message": "Success", "story_url": request.story_images, "webhook_url": request.webhook_url, "voice": request.voice}
    except Exception as e:
        log_url_template = "https://console.cloud.google.com/logs/query;query=resource.type%3D\"gae_app\"%20resource.labels.module_id%3D\"{service_id}\"%20resource.labels.version_id%3D\"{version_id}\"?project={project_id}"

        log_url = log_url_template.format(service_id=os.environ.get('GAE_SERVICE'), version_id=os.environ.get('GAE_VERSION'), project_id=os.environ.get('GOOGLE_CLOUD_PROJECT'))

        raise HTTPException(status_code=400, detail=f'Encountered a fatal error, you can see the logs here:\n{log_url}\nerror message: {e}')


@app.post("/transcription_webhook")
async def transcription_webhook(request: Request):
    body = await request.body()
    # Validate that the data structure matches what we expect
    try:
        data = json.loads(body, strict=False).get('data')
    except Exception as e:
        message = "Couldn't parse request body"
        log.error(message, e)
        raise HTTPException(status_code=400, detail=message)

    try:
        transcription = data.get('results').get('transcription')

        # Check if the "transcription" part exists and process it accordingly
        if transcription:
            log.info(f"Transcription: {transcription}")

            # Process the transcription part here
            storage_client = storage.Client()
            bucket = storage_client.bucket(os.getenv('GCS_BUCKET_NAME'))
            blob = bucket.blob(Path(data.get('job_id')) / SRT_FILE)
            blob.upload_from_string(transcription)
            log.info(f"Transcription: {data.get('results').get('transcription')}")

            # Respond that the request was processed successfully
            return {"message": "Transcription processed successfully."}
        else:
            # If there is no transcription, you might want to return a different message
            return {"message": "No transcription to process."}
    except Exception as e:
        message = "Couldn't find transcription in request"
        log.error(message, e)
        raise HTTPException(status_code=400, detail=message)


@app.get("/")
async def read_items():
    """
    This function expects for a story url and a webhook url to notify when it's done
    """

    return {"hello": "world"}

import traceback
from datetime import datetime

import requests
from google.cloud import storage
import json
import os
from pathlib import Path
from typing import Optional, Dict, Any, List

from dotenv import load_dotenv
from fastapi import FastAPI, Query, Depends, Request, HTTPException
from pydantic import BaseModel, HttpUrl, Field
from enum import Enum

from config import SRT_FILE
from src.log import log
from src.manager import Manager

load_dotenv()  # This loads the variables from '.env' into the environment
app = FastAPI()


class VoiceOption(str, Enum):
    male = "male"
    female = "female"
    custom = "custom"


class StoryToVideoRequest(BaseModel):
    story_images: List[HttpUrl] = Query(..., description="An ORDERED list of image URLs")
    script: str = Field(None, description="The script of the story")
    callback_url: Optional[HttpUrl] = Field(None, description="The callback URL to notify when processing is done")
    voice: Optional[VoiceOption] = Field(None, description="The voice to be used for narration")


@app.get('/test_gcs')
async def test_gcs():
    try:
        payload = 'hello world'

        # Process the transcription part here
        storage_client = storage.Client()
        bucket = storage_client.bucket(os.getenv('GCS_BUCKET_NAME'))
        blob = bucket.blob(f'test_gcs-{datetime.now()}')
        blob.upload_from_string(payload)
        return {'success': "motherfucker"}
    except Exception as e:
        return {'exception': str(e)}


@app.post("/story_to_video")  # Note the change to @app.post()
async def story_to_video(request: StoryToVideoRequest):  # The request parameter is now a Pydantic model, indicating a JSON body
    """
    This function expects a JSON body with a story URL, an optional webhook URL, and an optional voice option to notify when it's done.
    """
    try:
        # TODO: voice
        result = Manager().manage(request.story_images)
        result.update({"message": "Success"})

        try:
            if request.callback_url:
                requests.post(request.callback_url, data=result)
        except Exception as e:
            log.error("Couldn't post to callback url", e)

        return result
    except Exception as e:
        message = f'Encountered a fatal error: {str(e)} -> {traceback.print_exc()}'
        log.error(message, e)
        raise HTTPException(status_code=400, detail=message)


@app.post("/transcription_webhook")
async def transcription_webhook(request: Request):
    log.info(f'Transcription webhook got request: {request}')
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
            blob = bucket.blob(str(Path(data.get('job_id')) / SRT_FILE))
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

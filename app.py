import asyncio
import sys
import traceback
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime

import httpx
import requests
from google.cloud import storage
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, Query, Depends, Request, HTTPException, BackgroundTasks


from config import SRT_FILE, BASE_DIR, GCS_BUCKET_NAME, logger_with_id, set_logger
from src.captions_generator import CaptionsGenerator
from src.manager import Manager
from src.story_to_video_request import StoryToVideoRequest

load_dotenv()  # This loads the variables from '.env' into the environment
app = FastAPI()
set_logger()


@app.get('/test_gcs')
async def test_gcs():
    try:
        payload = 'hello world'

        # Process the transcription part here
        storage_client = storage.Client()
        bucket = storage_client.bucket(GCS_BUCKET_NAME)
        blob = bucket.blob(f'test_gcs-{datetime.now()}')
        blob.upload_from_string(payload)
        return {'success': "motherfucker"}
    except Exception as e:
        return {'exception': str(e)}


async def process_story_to_video(request: StoryToVideoRequest):
    result = {}
    try:
        # TODO: voice
        result = Manager().manage(request)
        result.update({"message": "Success"})

        try:
            if request.callback_url:
                requests.post(request.callback_url, data=result)
        except Exception as e:
            logger_with_id.error(f"Couldn't post to callback url: {str(e)} -> {traceback.print_exc()}")

        return result
    except Exception as e:
        message = f'Encountered a fatal error: {str(e)} -> {traceback.print_exc()}'
        logger_with_id.error(message)
        result = {"message": message}
    finally:
        if not request.callback_url:
            return
        async with httpx.AsyncClient() as client:
            response = await client.post(str(request.callback_url), json=result)
            print("Webhook response:", response.status_code, response.text)


@app.post("/story_to_video")  # Note the change to @app.post()
async def story_to_video(background_tasks: BackgroundTasks, request: StoryToVideoRequest):  # The request parameter is now a Pydantic model, indicating a JSON body
    """
    This function expects a JSON body with a story URL, an optional webhook URL, and an optional voice option to notify when it's done.
    """
    background_tasks.add_task(process_story_to_video, request=request)
    return {"message": "Processing"}


@app.post("/transcription_webhook")
async def transcription_webhook(request: Request):
    body = await request.body()
    logger_with_id.info(f'Transcription webhook got request: {body}')

    # Validate that the data structure matches what we expect
    try:
        data = json.loads(body, strict=False).get('data')
    except Exception as e:
        message = "Couldn't parse request body"
        logger_with_id.error(message)
        raise HTTPException(status_code=400, detail=message)

    try:
        transcription = data.get('results').get('transcription')
        transcription = CaptionsGenerator.generate_highlighted_captions(transcription)

        if transcription:
            video_dir = BASE_DIR / data.get('job_id')
            if not os.path.exists(str(video_dir)):
                os.makedirs(video_dir)
            with open(str(video_dir / SRT_FILE), 'w') as f:
                f.write(transcription)
            # Process the transcription part here
            storage_client = storage.Client()
            bucket = storage_client.bucket(GCS_BUCKET_NAME)
            blob = bucket.blob(str(Path(data.get('job_id')) / SRT_FILE))
            blob.upload_from_string(transcription)

            # Respond that the request was processed successfully
            return {"message": "Transcription processed successfully."}
        else:
            # If there is no transcription, you might want to return a different message
            message = "No transcription to process."
            logger_with_id.warning(message)
            return {"message": message}
    except Exception as e:
        message = "Couldn't generate transcription srt"
        logger_with_id.error(message + f'{str(e)} -> {traceback.print_exc()}')
        raise HTTPException(status_code=400, detail=message)


@app.get("/")
async def read_items():
    """
    This function expects for a story url and a webhook url to notify when it's done
    """

    return {"hello": "world"}

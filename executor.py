import datetime
import json
import logging
import pickle
import random
import time
import traceback
from concurrent.futures import TimeoutError, ThreadPoolExecutor
from google.cloud.pubsub_v1.subscriber.message import Message as PubSubMessage

import requests
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from google.cloud.pubsub import SubscriberClient
import os

from config import API_REQUEST_SUBSCRIPTION, PROJECT_ID, logger
from src.manager import Manager
from src.pydantic_models.api_message import ApiMessage
from src.pydantic_models.story_to_video_request import StoryToVideoRequest


class Executor:
    def __init__(self):
        self.executor = ThreadPoolExecutor(50)
        logging.getLogger('apscheduler.executors.default').setLevel(logging.ERROR)
        self.subscriber = SubscriberClient()

    def execute(self):
        subscription_path = self.subscriber.subscription_path(PROJECT_ID, API_REQUEST_SUBSCRIPTION)

        streaming_pull_future = self.subscriber.subscribe(subscription_path, callback=self.callback)

        logger.info(f"executor started, waiting for messages on {subscription_path}")
        with self.subscriber:
            streaming_pull_future.result()

    def callback(self, message: PubSubMessage):
        api_message: ApiMessage = pickle.loads(message.data)
        if api_message.sub_url == '/story_to_video':
            self.executor.submit(self.story_to_video, api_message.request, message)
        message.ack()

    def story_to_video(self, request: StoryToVideoRequest, message: PubSubMessage):
        start_time = time.time()

        result = {}
        try:
            temp_id = random.randint(100000, 999999)
            logger.set_id(_id=str(temp_id))
            logger.info(f"Story to video with payload {request}")

            # TODO: voice
            result = Manager().manage(request)
            logger.info(
                f"Successfully generated video -> {result}")

            result.update({"message": "Success"})
        except Exception as e:
            message = f'Encountered a fatal error: {str(e)} -> {traceback.print_exc()}'
            logger.error(message)
            result = {"message": message}
        finally:
            end_time = time.time()
            result['request'] = request.json()
            result['execution_time'] = end_time - start_time
            if not request.callback_url:
                logger.warning(f"callback url was not provided for result -> {result}")
            else:
                requests.post(str(request.callback_url), json=result)
            # message.ack()


if __name__ == "__main__":
    Executor().execute()
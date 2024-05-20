import asyncio

import pytest

from app import transcription_webhook
from config import logger
from src.narrator import Narrator
from src.script_generator import ScriptGenerator
from tests.test_app import get_random_voice

class MockRequest:
    def __init__(self, body):
        self._body = body

    async def body(self):
        return self._body


def mock_request():
    # Create a mock response object
    transcription_request = '{"data": {"job_id": "zM4HWKiGNBCAQ3Bce7", "input": {"filename": "zM4HWKiGNBCAQ3Bce7.mp3", "url": "https://peregrine-results.s3.amazonaws.com/zM4HWKiGNBCAQ3Bce7.mp3"}, "results": {"format": "SRT", "word_level": true, "segment_level": false, "webhook_url": "https://webhook.site/03ad89e5-c33c-4437-b2a0-0f8ea0ec383e", "status": "complete", "started": "2024-05-17 12:27:37.510464", "completed_at": "2024-05-17 12:27:40.621796", "_links": [{"href": "http://127.0.0.1:8080/transcribe/result/zM4HWKiGNBCAQ3Bce7", "method": "GET", "contentType": "application/json", "rel": "self", "description": "Collect transcription JSON payload results"}], "transcription": "0\n00:00:00,040 --> 00:00:00,200\nGet\n\n1\n00:00:00,200 --> 00:00:00,560\nready\n\n2\n00:00:00,560 --> 00:00:00,720\nfor\n\n3\n00:00:00,720 --> 00:00:00,840\nthe\n\n4\n00:00:00,840 --> 00:00:01,360\nwildest\n\n5\n00:00:01,360 --> 00:00:01,600\nride\n\n6\n00:00:01,600 --> 00:00:01,720\nof\n\n7\n00:00:01,720 --> 00:00:01,860\nyour\n\n8\n00:00:01,860 --> 00:00:02,260\nlife\n\n9\n00:00:02,260 --> 00:00:02,460\nwith\n\n10\n00:00:02,460 --> 00:00:03,100\nMAWARES,\n\n11\n00:00:03,500 --> 00:00:03,960\nMartian\n\n12\n00:00:03,960 --> 00:00:04,360\nAlien\n\n13\n00:00:04,360 --> 00:00:04,760\nRampage\n\n14\n00:00:04,940 --> 00:00:05,340\nSquad.\n\n15\n00:00:06,040 --> 00:00:06,160\nFollow the\n\n16\n00:00:06,200 --> 00:00:06,520\nfearless\n\n17\n00:00:06,520 --> 00:00:06,940\nsoldiers\n\n18\n00:00:06,940 --> 00:00:07,120\nof\n\n19\n00:00:07,120 --> 00:00:07,240\nthe\n\n20\n00:00:07,240 --> 00:00:07,640\nMAARs\n\n21\n00:00:07,740 --> 00:00:07,960\nteam\n\n22\n00:00:07,960 --> 00:00:08,060\nas\n\n23\n00:00:08,120 --> 00:00:08,240\nthey\n\n24\n00:00:08,240 --> 00:00:08,620\nbattle\n\n25\n00:00:08,620 --> 00:00:09,540\notherworldly\n\n26\n00:00:09,540 --> 00:00:10,000\ninvaders\n\n27\n00:00:10,080 --> 00:00:10,240\nfrom\n\n28\n00:00:10,240 --> 00:00:10,360\nthe\n\n29\n00:00:10,360 --> 00:00:10,480\nRed\n\n30\n00:00:10,540 --> 00:00:11,160\nPlanet.\n\n31\n00:00:11,840 --> 00:00:12,260\nExplosive\n\n32\n00:00:12,260 --> 00:00:12,640\naction,\n\n33\n00:00:13,000 --> 00:00:13,160\nmind\n\n34\n00:00:13,160 --> 00:00:13,440\n-blowing\n\n35\n00:00:13,440 --> 00:00:13,700\ntech\n\n36\n00:00:13,820 --> 00:00:14,180\nand\n\n37\n00:00:14,180 --> 00:00:14,400\njaw\n\n38\n00:00:14,400 --> 00:00:14,800\n-dropping\n\n39\n00:00:14,800 --> 00:00:15,220\ntwists\n\n40\n00:00:15,240 --> 00:00:15,520\nawait\n\n41\n00:00:15,520 --> 00:00:15,740\nyou\n\n42\n00:00:15,800 --> 00:00:16,060\nin\n\n43\n00:00:16,120 --> 00:00:16,460\nevery\n\n44\n00:00:16,460 --> 00:00:16,820\nissue.\n\n45\n00:00:17,140 --> 00:00:17,400\nDon\'t\n\n46\n00:00:17,400 --> 00:00:17,660\nmiss\n\n47\n00:00:17,660 --> 00:00:17,860\nout\n\n48\n00:00:17,860 --> 00:00:18,000\non\n\n49\n00:00:18,000 --> 00:00:18,100\nthe\n\n50\n00:00:18,100 --> 00:00:18,460\nintergalactic\n\n51\n00:00:18,720 --> 00:00:19,140\nmayhem\n\n52\n00:00:19,140 --> 00:00:19,320\nwith\n\n53\n00:00:19,360 --> 00:00:20,010\nMAARAS."}}}'
    return MockRequest(transcription_request)

def test_captions():
    request = mock_request()
    response = asyncio.run(transcription_webhook(request))

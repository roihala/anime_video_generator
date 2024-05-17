import json
import os
import requests
from dotenv import load_dotenv

from config import VOICES_JSON

load_dotenv()  # This loads the variables from '.env' into the environment

url = "https://api.play.ht/api/v2/voices"

headers = {
    "accept": "application/json",
    "AUTHORIZATION": os.getenv("PLAY_HT_API_KEY"),
    "X-USER-ID": os.getenv("PLAY_HT_USER_ID")
}

response = requests.get(url, headers=headers)

with open(VOICES_JSON, 'w') as f:
    f.write(json.dumps(response.json()))

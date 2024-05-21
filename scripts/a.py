import json

from config import VOICES_JSON

with open(VOICES_JSON, 'r') as f:
    voices = json.loads(f.read())

for i in range(len(voices)):
    print(voices[i].get('sample'))
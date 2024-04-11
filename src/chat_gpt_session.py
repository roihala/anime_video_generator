#
#  chat_gpt_session.py
#
#  Created by Eldar Eliav on 2023/05/11.
#
import base64
import os
from dotenv import load_dotenv

load_dotenv()  # This loads the variables from '.env' into the environment
os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')

from openai import OpenAI

class ChatGPTSession:
    def __init__(self, system_message: str):
        self._set_system_message(system_message)
        # new
        # TODO: api key
        decoded_key = base64.b64decode(os.getenv('OPENAI_API_KEY')).decode()
        self._client = OpenAI(api_key=decoded_key)
        self._chat_log = []

    # api methods
    def ask(self, question: str) -> str:
        self._chat_log.append({
            'role': 'user',
            'content': question
        })
        self._completion = self._client.chat.completions.create(model='gpt-3.5-turbo', messages=self._chat_log)
        answer = self._completion.choices[0].message.content

        self._chat_log.append({
            'role': 'assistant',
            'content': answer
        })
        return answer

    def get_last_answer(self) -> str:
        for entry in self._chat_log[::-1]:
            if entry['role'] == 'user':
                return entry['content']
        return None

    # private methods
    def _set_system_message(self, message: str):
        self._chat_log = [{
            'role': 'system',
            'content': message
        }]

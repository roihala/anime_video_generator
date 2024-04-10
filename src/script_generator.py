#
#  script_generator.py
#
#  Created by Eldar Eliav on 2023/05/11.
#
import os

from src.chat_gpt_session import ChatGPTSession
from src.log import log
import os


class ScriptGenerator:
    # init
    def __init__(self):
        self._session = self._prepare_session()

    # api methods
    def generate(self) -> str:
        description = self._make_description()
        if os.getenv('DEBUG'):
            log.info(f"DESCRIPTION:\n{description}")
        return description

    # private methods
    def _prepare_session(self):
        return ChatGPTSession(
            """
You are a professional tiktok creator, you know how to create engaging videos.
            """
        )

    def _make_description(self) -> str:
        return self._session.ask(
            """
Write a short random comic book caption

- it should come down to 17-23 seconds length
- make it sound edgy, spicy and populistic.
- Acronym words must be with dots between the letters. Example: "AI" -> "A.I", "ASI" -> "A.S.I", etc.
            """
        )

#
#  script_generator.py
#
#  Created by Eldar Eliav on 2023/05/11.
#
from config import logger
from src.chat_gpt_session import ChatGPTSession
import os


class ScriptGenerator:
    # init
    def __init__(self):
        self._session = self._prepare_session()

    # api methods
    def generate(self, prompt) -> str:
        description = self._make_description(prompt)
        if os.getenv('DEBUG'):
            logger.info(f"DESCRIPTION: {description}")
        return description

    # private methods
    def _prepare_session(self):
        return ChatGPTSession(
            """
You are a professional YouTube shorts creator, you know how to create engaging videos.
            """
        )

    def _make_description(self, prompt=None) -> str:
        prompt = prompt if prompt else "Random book"
        return self._session.ask(
            f"""
Write a short description for this comic book: {prompt}

- it should come down to 17-23 seconds length
- make it sound edgy, spicy and populistic.
- Acronym words must be with dots between the letters. Example: "AI" -> "A.I", "ASI" -> "A.S.I", etc.
            """
        )

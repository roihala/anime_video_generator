#
#  script_generator.py
#
#  Created by Eldar Eliav on 2023/05/11.
#

from chat_gpt_session import ChatGPTSession
from log import log

# TODO - write the output strings to files, destination will be provided from the outside for each file

class ScriptGenerator:
    # init
    def __init__(self):
        self._session = self._prepare_session()

    # api methods
    def generate(
        self,
        channel_name: str,
        topic: str,
        is_verbose_print: bool = False
    ) -> (str, str, str):
        # script = self._make_script(topic, channel_name)
        # captions = self._make_captions()
        description = self._make_description()
        if is_verbose_print:
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

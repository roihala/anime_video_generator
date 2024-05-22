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
    def generate(self, prompt, images_count) -> str:
        description = self._make_description(prompt, images_count)
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

    def _make_description(self, title, images_count) -> str:
        # Title is ignored
        title = title if title else "Random book"
        return self._session.ask(
            f"""Act like an experienced social media expert with over 20 years of TikTok marketing experience. You work at Toontube, a comics platform hosting new comics and manga titles. Your goal is to create perfect TikTok teaser scripts for each new comic.

First, I'll provide the comic synopsis. 
Based on this, you will create a voice narrative script.
TikTok teasers account for 80% of a comic's sales, so perfection is crucial.

Here’s the synopsis:

//synopsis//
"What will you do when mankind’s scientific overreach causes the destruction of civilization as we know it, and the powers that be strain to hold on to any last vestige of control? It may be necessary to use the very technology that brought apocalypse, in order to find a path forward in a world where mutants and disease reign supreme. Even if that means venturing into the enclave.

Join us to follow our unlikely hero, a child in a GP-5, throughout his mysterious encounters with the new mutant residents of post-apocalyptic soviet-era apartment buildings."
//synopsis//

A perfect teaser should include:

- Trigger: An attention-grabbing opening line or image.
- Action: Clear instructions on what the audience should do next.
- Variable Reward: A hint of the comic's appeal (mystery, adventure, character depth).
- Call to Action: A clear and enticing next step for the audience, such as "Read on Toontube."

Guidelines:

- Be creative, ear-catching, and evoke emotion.
- Use hooks to maintain attention beyond 8 seconds.
- Avoid jargon, fancy words, questions, and emojis. Use simple, conversational English.
- The script should be up to 55 seconds long.
- Create two versions with different narratives.
- Mention the studio's name, Molot Comics.

Suggestions:

- Provide clear, simple actions tailored to the comic’s theme.
- Highlight unique aspects of the comic to hint at its appeal.
- Ensure the Call to Action is simple and direct.
- Incorporate hooks around the 8-second mark to maintain viewer engagement."""
        )

"""
This is the brain of the bot. It decides what to do with a message.

For now the bot performs a semantic search of prior messages and injects this into a message to GPT-3.
That message is further modified by the attitude module.

To-to: This file should keep track of recent user interactions (FIFO) and also inject those into the prompt.
Typically chat bots also keep track of the bot's own output so we should do that too. It is debatable whether channel chat
history other than bot interactions should be included. If it's semantically relevant it'll be injected anyway.

"""
from bazbot.vectors import Vectinator
from bazbot.attitude import BazAttitude
import openai
from os import getenv
from dotenv import load_dotenv

load_dotenv()
openai.api_key = getenv("OPENAI_API_KEY")

if openai.api_key is None:
    print("OPENAI_API_KEY is not set in .env file.")
    exit(1)


class BazBrain:
    def __init__(self):
        self.vectinator = Vectinator()
        self.attitude = BazAttitude()

    async def _gpt_request(self, prompt: str) -> str:
        completion = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
        )
        #print('completion:', completion)
        return completion.choices[0].message.content # type: ignore (openai's python binding is hot garbage')

    async def think(self, author: str, channel: str, message: str) -> str | None:
        """Return the bot's response to the message. Can return None if it chooses to ignore the message"""
        message_no_prefix = message.split("!baz")[1].strip()
        prompt = author + " in " + channel + " says to you: " + message_no_prefix + "\n"
        # If we got got semantically relevant search results, stick those in the prompt
        results = self.vectinator.search(message_no_prefix)
        if len(results) > 0:
            prompt +=  f"Consider possibly relevant old posts that {author} will not remember:\n"
            for result in results:
                prompt += (
                    f"{result.author_name} in the {result.channel} channel said: {result.message}\n"
                )
        # Now make a prompt from our attitude module
        fullprompt = self.attitude.make_prompt(prompt)
        print('prompt:', fullprompt)
        try:
            response = await self._gpt_request(fullprompt)
            processed_response = self.attitude.process_response(response)
            return processed_response
        except Exception as e:
            print(e)
            return None

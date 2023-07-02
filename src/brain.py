"""
This is the brain of the bot. It decides what to do with a message.

We could actually expose the search functionality via a web API and use GPT's function calling:
https://openai.com/blog/function-calling-and-other-api-updates

But for now, we'll just do something super basic and do a semantic search for the messages.

"""
from vectors import Vectinator
from attitude import BazAttitude
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
        prompt = (
            "Bogan member " + author + " in " + channel + " says to you: " + message_no_prefix + "\n"
        )
        results = self.vectinator.search(message)
        # If we got got semantically relevant search results, stick those in the prompt
        if len(results) > 0:
            prompt +=  "Potentially relevant past posts by Maker Bogan members: \n"
            for result in results:
                prompt += (
                    f"{result.author_name} in {result.channel} said: {result.message}\n"
                )
        # Now make a prompt from our attitude module
        fullprompt = self.attitude.make_prompt(prompt)
        print('prompt:', fullprompt)
        try:
            response = await self._gpt_request(fullprompt)
            return response
        except Exception as e:
            print(e)
            return None

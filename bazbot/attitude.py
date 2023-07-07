"""
This is responsible for injecting some personality into the bot's responses.

We try to make the bot's responses dependent on its mood, and we inject some beliefs into the context at random to mix things up.
The relevant data for this is in attitudes.json
"""
import json
from typing import TypedDict
from random import choice
from os.path import join, dirname
import re

class BotAttitude(TypedDict):
    name: str
    p: str

class AttitudeData(TypedDict):
    basic: str
    moods: list[BotAttitude]
    beliefs: list[BotAttitude]

class BazAttitude:
    def __init__(self):
        jsonfilename = join(dirname(__file__), 'attitudes.json')
        self.data: AttitudeData = json.load(open(jsonfilename, 'r'))
        self.current_mood = 'default'
        # make a mapping of mood names to mood statements
        self.moods: dict[str, str] = {} 
        for mood in self.data['moods']:
            self.moods[mood['name']] = mood['p']

    def make_prompt(self, message: str) -> str:
        """Create the prompt to be used for the LLM."""
        # First use the basic bot attitude and then add a random belief. Baz thinks faster than puny humans.
        prompt = self.data['basic'] + " " + choice(self.data['beliefs'])['p'] + "\n"
        # Tell LLM about possible moods.
        all_moods = ", ".join(self.moods.keys())
        prompt += f"From possible moods modes {all_moods}, your current mood [mood mode: {self.current_mood}]. "
        # Now add the statement of the current mood
        prompt += self.moods[self.current_mood] + "\n"
        # Now add the message we're responding to
        prompt += message + "\n"
        # And finally a direction in how to response, and how to change the mood mode so it is responsive to users.
        prompt += "Respond appropriately in no more than five sentences. If you want to change your mood mode, say: [mood mode: <mood mode>].\n"
        return prompt

    def _change_mood(self, mood: str):
        """Change the mood of the bot."""
        if mood in self.moods:
            self.current_mood = mood
        
    def process_response(self, response: str) -> str:
        # Find all occurences of [mood mode: <mood mode>]
        matches = re.findall(r'\[mood mode: (.*?)\]', response)
        # For each match, call change_mode function
        for match in matches:
            self._change_mood(match)
        # Remove all occurrences of the pattern from the string
        processed_string = re.sub(r'\[mood mode: (.*?)\]', '', response)
        return processed_string

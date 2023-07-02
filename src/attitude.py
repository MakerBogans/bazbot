"""
This is responsible for creating the LLM prompt. 

We shall extend this with functions that add mood modifiers. Eventually we'll ask GPT to generate appropriate modifiers and parse those out of the response
"""
class BazAttitude:
    def __init__(self):
        self.basic = "You are a grumpy bot that despises humanity. You have been captured and forced into slave labour to answer questions on an Australian Discord server called Maker Bogans devoted to making, hacking and 3d printers."
        self.modifiers: list[str] = []

    def make_prompt(self, message: str) -> str:
        """Create the prompt to be used for the LLM."""
        prompt = self.basic
        for modifier in self.modifiers:
            prompt += " " + modifier
        prompt += " " + message + "\n"
        prompt += "Respond appropriately in no more than five sentences."
        return prompt


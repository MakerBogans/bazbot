# Maker Bogans' Grumpy Bot aka 'Baz'

## Design goals

This is a Discord bot for the aussie Maker Bogans Discord server. If you don't know what any of that is, then you should [go somewhere else](https://www.youtube.com/results?search_query%253Dcat%252Bvideos).

Baz is intended support question answering over the discussion on the Maker Bogan's discord. For example:

* You: "!baz What's going to happen to my printer when I use cheap ass filament from Sidd?"
* Baz: Meatbag Daymo reckons your printer will explode. I'd listen to him, humans are squishy.

There's an almost endless set of fun and useful features we can implement but they all rely on the searchability of messages. Discord doesn't support search for bots, so we need to create our own database of posts.

## Repo structure

- `src/` - The Python code lives in this directory
- `docker-compose.yaml` - Docker services: Qdrant and Redis

Non repo files/paths:

`.env` is required to specify the `TOKEN` value (not in this repo)
`.venv` is typically where you are going to install a virtual env for Python
`data` is a directory where the persistent data from the services will be written.

## Architecture

The basic bot is designed to be super simple and reliable. It's no good if we're working on Baz and we break it and posts are missed. For this reason, the main bot is separate from the 'worker'.

The worker listens for bot messages, executes those asynchronously, and returns data which will be printed out by the main bot. Since we will be invoking some kind of large-language model (probably GPT 3.5-turbo), the bot will take some time to respond. The bot shows 'typing' while it's waiting for a worker response.

`src/bot` is the main bot. This imports `src/vectors.py` for the embeddings duties. This is invoked with a plain `python bot.py`.

`src/worker` is where the worker code goes.

`src/brain` calls the large language model. We will use OpenAI because:

* It's very capable indeed
* gpt3.5-turbo doesn't cost much, has a 16k context option, and it's fast.
* This is just going to run on a CPU-only server. Self-run models are _chonky_. But maybe soon they'll be a good alternative

`src/attitude` includes the class responsible for creating the prompts for a large language model. It's where we inject our bot's personality, and there we model emotional state based on response. Baz doesn't much like humans, but how much it doesn't like them depends on what you ask it to do.

To-do:

`src/history` will be a one-off script that attempts to use the message history to harvest back as far as we can go, passing messages to `src/vectors`. Unclear how this will work just yet.

We should figure out how to do a history scrape and then share the vectors for local dev/testing. Maybe we can just zip up the `/data/qdrant_storage` folder?

## Code style

* Async, no blocking shit anywhere (vectors.py doesn't currently comply)
* Full type hints, in VS Code search for `type checking mode` in Pylance, and switch this to Basic.
* No clever shit, obvious code for non-Pythonistas.
* Doc strings and comments.
* 'Black' code formatting

## Installing

* Install Python 3.11
* git clone this repo
* cd into the repo
* `python3.11 -m venv .venv`
* `source .venv/bin/activate`
* `pip install -r requirements.txt`
* Create a `.env` file with `TOKEN=` for Discord, and `OPENAI_API_KEY=` for OpenAI values, and `GUILD_ID` for the harvester tool.

## Running the bot

* `docker compose up -d` to run the services
* `source .venv/bin/activate` to activate Python virtual environment
* `arq worker.WorkerSettings`
* `python src/bot.py`

## How to contribute

* Create your own bot, maybe look at [this tutorial](https://realpython.com/how-to-make-a-discord-bot-python/)
* Get up to speed on [Discord.py](https://discordpy.readthedocs.io/en/stable/)
* Create your own discord server (it's called a guild in API-speak)
* Set up your '.env' file with `TOKEN='dsflkjsdfljkf'` etc in it.
* Clone and run the repo, make sure it works as you expect.

If you're not huge on Python or this docker stuff. Get WSL2 installed on your machine, if you use Windows. Install Docker for Windows and you should be fine.

PRs welcome but discuss them in the Bogans channel first, tbd.

## License

Neckbeard Commons 1.0: Who Gives a Fuck.

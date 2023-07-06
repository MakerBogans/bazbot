from asyncio import sleep
from bazbot.brain import BazBrain

brain = BazBrain()


async def command(ctx: dict, author: str, channel: str, message: str) -> str | None:
    """This is the worker function that will be called by the arq worker."""
    response = await brain.think(author, channel, message)
    return response


# WorkerSettings defines the settings to use when creating the work,
# it's used by the arq cli.
# For a list of available settings, see https://arq-docs.helpmanual.io/#arq.worker.Worker
class WorkerSettings:
    functions = [command]

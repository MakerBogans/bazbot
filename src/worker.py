from asyncio import sleep

async def command(ctx: dict, message: str) -> str:
    await sleep(2)
    return f"Worker response to {message}"

# WorkerSettings defines the settings to use when creating the work,
# it's used by the arq cli.
# For a list of available settings, see https://arq-docs.helpmanual.io/#arq.worker.Worker
class WorkerSettings:
    functions = [command]

#!/bin/bash
source .venv/bin/activate
arq bazbot.worker.WorkerSettings --watch bazbot/ &
python -m bazbot.bot

import asyncio
from loguru import logger
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import datetime

import tasks
import tasks.eth



if __name__ == "__main__":
    logger.info("Starting scheduler")

    # Add task
    scheduler = AsyncIOScheduler()

    scheduler.start()

    asyncio.get_event_loop().run_forever()

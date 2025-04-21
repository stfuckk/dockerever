import asyncio
import logging

from src.db.init_db import init_db
from src.db.init_db import __create_main_dashboard
from src.db.database import get_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def init() -> None:
    async with get_db() as db:
        await init_db(db)
        await __create_main_dashboard(db)


async def main() -> None:
    logger.info("Creating initial data")
    await init()
    logger.info("Initial data created")


if __name__ == "__main__":
    asyncio.run(main())

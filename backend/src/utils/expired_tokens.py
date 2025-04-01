from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from src.db.database import get_db
from src.datasources.token_pair import token_pair_datasource
import src.config as settings
import logging

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()

hour = settings.EXPIRED_TOKENS_CRON_HOUR


async def remove_expired_tokens() -> None:
    """
    Задача для удаления просроченных токенов.
    """
    async with get_db() as db:
        logger.info("Task started: deleting expired tokens...")
        await token_pair_datasource.delete_expired_tokens(db)
        logger.info("Task finished: expired tokens deleted.")


def start_scheduler() -> None:
    """
    Настройка и запуск планировщика задач.
    """
    print(settings.TIMEZONE)
    scheduler.add_job(
        remove_expired_tokens,
        trigger=CronTrigger(hour=hour, minute="0", timezone=settings.TIMEZONE),  # Запуск каждый час
        id="remove_expired_tokens",
        replace_existing=True,
    )
    scheduler.start()
    logger.info(f"Remove expired tokens task scheduled. The next fire time is {scheduler.get_jobs()[-1].next_run_time}")

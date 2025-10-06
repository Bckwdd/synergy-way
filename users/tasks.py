import logging

from celery import Celery
from celery.schedules import crontab

from core.config import settings
from core.database import session_factory
from users.infrastructure.api_client import FakerApiClient, JsonPlaceholderClient
from users.infrastructure.repository import UsersRepository
from users.service import UsersService

logger = logging.getLogger(__name__)

app = Celery("sync_tasks", broker=settings.celery_broker_url, include=["users.tasks"])

app.conf.beat_schedule = {
    "sync-users": {
        "task": "tasks.sync_users_task",
        "schedule": crontab(minute="*"),
    },
}

app.conf.timezone = "Europe/Kyiv"


@app.task(name="tasks.sync_users_task", bind=True, max_retries=3)
def sync_users_task(self):
    """
    Celery task for periodic synchronization of user data from external APIs
    to the PostgreSQL database.

    This task manages the database transaction and handles retry logic upon failure.

    :param self: The bound Celery task instance, used for access to request info and retry method.
    :raises Retry: Reraises the Celery Retry exception if synchronization fails, triggering a retry after a cooldown.
    :return: A status string indicating the number of users processed.
    """
    task_id = self.request.id
    logger.debug("[%s] Starting periodic user data sync...", task_id)

    user_client = JsonPlaceholderClient()
    credit_card_client = FakerApiClient()

    try:
        with session_factory() as session:
            repository = UsersRepository(db=session)

            service = UsersService(
                repo=repository, user_client=user_client, credit_card_client=credit_card_client
            )

            created_users = service.sync_users()
            session.commit()

            logger.info(
                "[%s] Sync finished successfully. Total new users processed: %d",
                task_id,
                len(created_users),
            )
            return f"Total new users processed: {len(created_users)}"

    except Exception as exc:
        logger.warning("[%s] Database transaction rolled back due to error.", task_id)
        session.rollback()

        raise self.retry(exc=exc, countdown=60)

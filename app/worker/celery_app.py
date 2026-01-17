from app.config import Settings
from celery import Celery
from abc import ABC, abstractmethod



class BaseCeleryWorker(ABC):
    def __init__(self, settings: Settings):
        self.settings = settings
        self.celery_app = self._create_celery_app()

    @abstractmethod
    def _create_celery_app(self) -> Celery:
        pass


class CeleryDerebitWorker(BaseCeleryWorker):
    def __init__(self, settings: Settings):
        super().__init__(settings)
        self.celery_app = self._create_celery_app()

    def _create_celery_app(self) -> Celery:
        celery_app = Celery(
            "deribit_worker",
            broker=self.settings.redis_url,
            backend=self.settings.redis_url
        )

        celery_app.conf.update(
            task_serializer="json",
            accept_content=["json"],
            result_serializer="json",
            timezone="UTC",
            enable_utc=True,
            beat_schedule={
                "fetch-prices-every-minute": {
                    "task": "app.worker.tasks.DerebitTaskManager.create_task_fetch_price",
                    "schedule": 60.0,
                },
            },
            task_track_started=True,
            task_time_limit=30,
            worker_max_tasks_per_child=100,
        )

        return celery_app

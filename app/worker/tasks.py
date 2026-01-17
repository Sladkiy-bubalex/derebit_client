from fastapi import FastAPI
from app.config import Settings
from app.worker.celery_app import CeleryDerebitWorker
from app.database.db import DatabaseManager
from app.database.repositories import PriceRepository
from loguru import Logger as LoguruLogger
from app.worker.services import DeribitClient, PriceFetcher
from celery import Celery
from abc import ABC, abstractmethod


class BaseTaskManager(ABC):
    """Абстрактный класс для менеджеров задач"""

    def __init__(self, *args, **kwargs):
        pass

    @abstractmethod
    def create_client(self):
        """Абстрактная фабрика для создания клиента"""
        pass

    @abstractmethod
    def create_price_fetcher(self, client):
        """Абстрактная фабрика для создания сборщика цен"""
        pass


class DerebitTaskManager(BaseTaskManager):
    """Менеджер Celery задач для Derebit"""

    def __init__(
        self,
        settings: Settings,
        database_manager: DatabaseManager,
        celery_app: Celery,
        price_repository: PriceRepository,
        logger: LoguruLogger
    ):
        self.settings = settings
        self.database_manager = database_manager
        self.celery_app = celery_app
        self.price_repository = price_repository
        self.logger = logger

    def create_client(self):
        return DeribitClient(base_url=self.settings.DERIBIT_BASE_URL)

    def create_price_fetcher(self, deribit_client: DeribitClient) -> PriceFetcher:
        return PriceFetcher(
            client=deribit_client,
            database_manager=self.database_manager,
            price_repository=self.price_repository,
            logger=self.logger
        )

    def create_task_fetch_price(self, celery_app: Celery):
        @celery_app.task(
            name="fetch_price",
            bind=True,
            max_retries=3,
            default_retry_delay=10
        )
        async def fetch_price(self):
            self.logger.info("Start fetch price task")

            deribit_client = self.create_client()
            price_fetcher = self.create_price_fetcher(deribit_client)

            currencies = ["BTC", "ETH"]

            results = await price_fetcher.fetch_and_save_prices(currencies)

            self.logger.info(
                f"Fetch price task completed."
                f"Success: {results['success']}"
                f"Failed: {results['failed']}"
            )

            return results

        return fetch_price


def create_derebit_task_manager(app: FastAPI) -> DerebitTaskManager:
    """Фабрика для создания DerebitTaskManager со всеми зависимостями"""

    task_manager = DerebitTaskManager(
        settings=app.state.settings,
        database_manager=app.state.db_manager,
        celery_app=CeleryDerebitWorker(app.state.settings).celery_app,
        price_repository=PriceRepository(app.state.db_manager.session),
        logger=app.state.logger
    )

    return task_manager

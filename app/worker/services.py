import aiohttp
from loguru import Logger as LoguruLogger
from typing import Dict, Any, List
from abc import ABC, abstractmethod
from datetime import datetime
from app.database.db import DatabaseManager
from app.database.repositories import PriceRepository


class BaseClient(ABC):
    """Базовый клиент для API"""

    def __init__(self, base_url: str):
        self.base_url = base_url
    

    @abstractmethod
    async def get_index_price(self, currency: str) -> Dict[str, Any]:
        """Абстрактный метод для получения индекса цены"""
        pass


class DeribitClient(BaseClient):
    """Сервис для запросов к Deribit API"""

    def __init__(self, base_url: str):
        super().__init__(base_url)

    async def get_index_price(self, currency: str) -> Dict[str, Any]:
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/get_index_price"
            params = {"index_name": f"{currency.lower()}_usd"}

            async with session.get(url, params=params) as response:
                data = await response.json()
                return data.get("result", {})


class PriceFetcher:
    """Сервис для получения и сохранения цен"""

    def __init__(
        self,
        client: BaseClient,
        database_manager: DatabaseManager,
        price_repository: PriceRepository,
        logger: LoguruLogger
    ):
        self.client = client
        self.database_manager = database_manager
        self.price_repository = price_repository
        self.logger = logger

    async def fetch_and_save_prices(self, currencies: List[str]) -> Dict[str, List[str]]:
        """Получение и сохранение цен"""
        results = {"success": [], "failed": []}

        for currency in currencies:
            try:
                self.logger.info(f"Fetching price for {currency}")
                data = await self.client.get_index_price(currency)

                if not data or "index_price" not in data:
                    self.logger.warning(f"No valid data for {currency}")
                    results["failed"].append(currency)
                    continue

                async with self.database_manager.get_session() as session:
                    await self.price_repository(session).create(
                        ticker=f"{currency}_usd",
                        price=float(data["index_price"]),
                        timestamp=int(datetime.now().timestamp())
                    )

                self.logger.info(f"Successfully saved {currency} price")
                results["success"].append(currency)

            except Exception as e:
                self.logger.error(f"Error processing {currency}: {e}")
                results["failed"].append(currency)

        return results

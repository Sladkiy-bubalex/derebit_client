from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models import PriceTick


class PriceRepository:
    """Репозиторий для работы с ценами"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, ticker: str, price: float, timestamp: int) -> PriceTick:
        """Создать запись"""
        price_tick = PriceTick(
            ticker=ticker,
            price=price,
            timestamp=timestamp
        )
        self.session.add(price_tick)
        await self.session.commit()
        await self.session.refresh(price_tick)
        return price_tick

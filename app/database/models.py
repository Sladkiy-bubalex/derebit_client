from sqlalchemy import Integer, String, Float
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped


class Base(DeclarativeBase):
    pass


class BaseModel(Base):
    __abstract__ = True

    id: Mapped[int] = mapped_column(Integer, primary_key=True)


class PriceTick(BaseModel):
    __tablename__ = "price_ticks"

    ticker: Mapped[str] = mapped_column(String, nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    created_at_timestamp: Mapped[int] = mapped_column(Integer, nullable=False)

    def __str__(self):
        return f"PriceTick(ticker='{self.ticker}', price={self.price})"

    def __repr__(self):
        return (f"<PriceTick(id={self.id},"
                f"ticker='{self.ticker}',"
                f"price={self.price},"
                f"created_at={self.created_at_timestamp})")

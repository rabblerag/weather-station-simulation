from sqlalchemy import String, TIMESTAMP, JSON
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

class Base(DeclarativeBase):
    pass

class Metric(Base):
    __tablename__ = "metrics"

    id : Mapped[int] = mapped_column(primary_key=True)
    station_id : Mapped[str] = mapped_column(String(16))
    timestamp : Mapped[str] = mapped_column(TIMESTAMP(True))
    data : Mapped[dict] = mapped_column(JSON())

    def __repr__(self):
        return f"Metric(id={self.id!r}, station_id={self.station_id!r}, timestamp={self.timestamp!r}, data={self.data!r})"


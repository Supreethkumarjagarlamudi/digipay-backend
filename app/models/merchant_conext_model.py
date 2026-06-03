from sqlalchemy import Column, Float, ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Boolean
from sqlalchemy import DateTime

from datetime import datetime

from app.database import Base

class MerchantContext(Base):

    __tablename__ = "merchant_context"

    id = Column(
        Integer,
        primary_key=True
    )

    merchant_id = Column(
        Integer,
        ForeignKey("merchants.id")
    )

    latitude = Column(Float)

    longitude = Column(Float)

    altitude = Column(Float)

    heading = Column(Float)

    speed = Column(Float)

    accuracy = Column(Float)

    timestamp = Column(
        DateTime,
        default=datetime.utcnow
    )
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Float
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey

from datetime import datetime

from app.database import Base


class Merchant(Base):

    __tablename__ = "merchants"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id")
    )

    business_name = Column(
        String(200),
        nullable=False
    )

    owner_name = Column(
        String(100),
        nullable=False
    )

    category = Column(
        String(100),
        nullable=False
    )

    gst_number = Column(
        String(50)
    )

    description = Column(
        String(500)
    )

    latitude = Column(Float)

    longitude = Column(Float)

    altitude = Column(Float)

    accuracy = Column(Float)

    heading = Column(Float)

    speed = Column(Float)

    upi_deep_link = Column(
        String(1000)
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )
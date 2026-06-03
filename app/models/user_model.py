from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Boolean
from sqlalchemy import DateTime

from datetime import datetime

from app.database import Base

class User(Base):

    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    phone_number = Column(
        String(20),
        unique=True,
        nullable=False
    )

    role = Column(
        String(20),
        default="customer"
    )

    full_name = Column(
        String(100),
        nullable=True
    )

    email = Column(
        String(100),
        nullable=True
    )

    profile_completed = Column(
        Boolean,
        default=False
    )

    is_verified = Column(
        Boolean,
        default=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )
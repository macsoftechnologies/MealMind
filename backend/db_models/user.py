from sqlalchemy import Column, Integer, String, Float, DateTime

from sqlalchemy.sql import func

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )
    email = Column(
        String,
        unique=True,
        index=True,
        nullable=True
    )

    password_hash = Column(
        String,
        nullable=True
    )

    name = Column(
        String,
        nullable=False
    )

    age = Column(
        Integer,
        nullable=False
    )

    gender = Column(
        String,
        nullable=False
    )

    height_cm = Column(
        Float,
        nullable=False
    )

    weight_kg = Column(
        Float,
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
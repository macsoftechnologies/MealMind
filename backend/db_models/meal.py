from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

from database import Base


class Meal(Base):
    __tablename__ = "meals"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )

    image_filename = Column(
        String,
        nullable=True
    )
    
    user_comment = Column(
        Text, 
        nullable=True)

    total_calories = Column(
        Float,
        nullable=False
    )

    total_protein_g = Column(
        Float,
        nullable=False
    )

    total_carbohydrates_g = Column(
        Float,
        nullable=False
    )

    total_fat_g = Column(
        Float,
        nullable=False
    )

    total_fiber_g = Column(
        Float,
        nullable=False
    )

    personalized_feedback = Column(
        JSONB,
        nullable=True
    )

    processing_time_seconds = Column(
        Float,
        nullable=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
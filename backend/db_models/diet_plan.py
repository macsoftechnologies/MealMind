from sqlalchemy import (
    Column,
    Date,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from database import Base


class DietPlan(Base):
    __tablename__ = "diet_plans"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # --------------------------------------------------------
    # USER
    # --------------------------------------------------------

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    # --------------------------------------------------------
    # USER DIET PREFERENCES
    # --------------------------------------------------------

    food_allergies = Column(
        JSONB,
        nullable=False,
        default=list
    )

    foods_to_avoid = Column(
        JSONB,
        nullable=False,
        default=list
    )

    meals_per_day = Column(
        Integer,
        nullable=False,
        default=4
    )

    # --------------------------------------------------------
    # CALCULATED NUTRITION TARGETS
    # --------------------------------------------------------

    bmr = Column(
        Float,
        nullable=False
    )

    tdee = Column(
        Float,
        nullable=False
    )

    target_calories = Column(
        Float,
        nullable=False
    )

    target_protein_g = Column(
        Float,
        nullable=False
    )

    target_carbohydrates_g = Column(
        Float,
        nullable=False
    )

    target_fat_g = Column(
        Float,
        nullable=False
    )

    target_fiber_g = Column(
        Float,
        nullable=False
    )

    # --------------------------------------------------------
    # GENERATED DIET PLAN
    # --------------------------------------------------------

    meals = Column(
        JSONB,
        nullable=False
    )

    daily_tip = Column(
        String,
        nullable=True
    )

    # --------------------------------------------------------
    # CREATED TIME
    # --------------------------------------------------------

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    week_start_date = Column(
        Date,
        nullable=True,
        index=True
    )

    week_end_date = Column(
        Date,
        nullable=True
    )

    weekly_plan = Column(
        JSONB,
        nullable=True
    ) 
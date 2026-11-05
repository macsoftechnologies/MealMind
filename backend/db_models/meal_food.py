from sqlalchemy import Column, Integer, String, Float, ForeignKey

from database import Base


class MealFood(Base):
    __tablename__ = "meal_foods"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    meal_id = Column(
        Integer,
        ForeignKey("meals.id"),
        nullable=False
    )

    food_name = Column(
        String,
        nullable=False
    )

    approximate_portion = Column(
        String,
        nullable=True
    )

    approximate_percentage = Column(
        Float,
        nullable=True
    )

    calories = Column(
        Float,
        nullable=False
    )

    protein_g = Column(
        Float,
        nullable=False
    )

    carbohydrates_g = Column(
        Float,
        nullable=False
    )

    fat_g = Column(
        Float,
        nullable=False
    )

    fiber_g = Column(
        Float,
        nullable=False
    )

    confidence_score = Column(
        Float,
        nullable=True
    )
from pydantic import BaseModel
from typing import List, Optional


# ============================================================
# FOOD ITEM
# ============================================================

class FoodItem(BaseModel):
    food_name: str
    approximate_portion: str
    approximate_percentage_of_visible_meal: float

    calories: float
    protein_g: float
    carbohydrates_g: float
    fat_g: float
    fiber_g: float

    confidence_score: float

    bounding_box: List[int]


# ============================================================
# MEAL TOTAL
# ============================================================

class MealTotal(BaseModel):
    calories: float
    protein_g: float
    carbohydrates_g: float
    fat_g: float
    fiber_g: float


# ============================================================
# PERSONALIZED FEEDBACK
# ============================================================

class PersonalizedFeedback(BaseModel):
    meal_overview: str
    whats_good: str
    what_to_consider: str
    suggestion: str
    healthy_add_on: str
    overall: str


# ============================================================
# COMPLETE MEAL RESPONSE
# ============================================================

class MealAnalysisResponse(BaseModel):
    foods: List[FoodItem]

    meal_total: MealTotal

    personalized_feedback: PersonalizedFeedback

    rest_of_day_advice: Optional[str] = None

    processing_time_seconds: float
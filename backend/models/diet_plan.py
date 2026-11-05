from pydantic import BaseModel, Field
from typing import List, Optional


# ============================================================
# DIET PLAN REQUEST
# ============================================================

class DietPlanCreate(BaseModel):
    food_allergies: List[str] = Field(default_factory=list)
    foods_to_avoid: List[str] = Field(default_factory=list)

    meals_per_day: int = Field(
        default=4,
        ge=3,
        le=6
    )


# ============================================================
# NUTRITION TARGETS
# ============================================================

class NutritionTargets(BaseModel):
    bmr: int
    tdee: int
    target_calories: int
    protein_g: int
    carbohydrates_g: int
    fat_g: int
    fiber_g: int


# ============================================================
# FOOD INSIDE A MEAL
# ============================================================

class DietFoodItem(BaseModel):
    food_name: str
    portion: str


# ============================================================
# INDIVIDUAL MEAL
# ============================================================

class DietMeal(BaseModel):
    meal_name: str
    foods: List[DietFoodItem]

    estimated_calories: float
    protein_g: float
    carbohydrates_g: float
    fat_g: float
    fiber_g: float


# ============================================================
# COMPLETE DIET PLAN RESPONSE
# ============================================================

class DietPlanResponse(BaseModel):
    user_id: int
    goal: str
    diet_preference: str | None

    nutrition_targets: NutritionTargets

    meals: List[DietMeal]

    daily_tip: str
    
from typing import List, Optional
from pydantic import BaseModel


class WeeklyMealItem(BaseModel):
    meal_type: str
    meal_name: str
    quantity: Optional[str] = None

    calories: Optional[float] = None
    protein_g: Optional[float] = None
    carbs_g: Optional[float] = None
    fat_g: Optional[float] = None


class WeeklyDayPlan(BaseModel):
    day_number: int
    day_name: str
    date: str

    meals: List[WeeklyMealItem]

    total_calories: Optional[float] = None
    total_protein_g: Optional[float] = None
    total_carbs_g: Optional[float] = None
    total_fat_g: Optional[float] = None


class WeeklyDietPlanResponse(BaseModel):
    week_start_date: str
    week_end_date: str

    days: List[WeeklyDayPlan]

    weekly_note: Optional[str] = None
from typing import Optional, Literal, List

from pydantic import BaseModel, Field


# ============================================================
# WOMEN'S HEALTH CONDITION
# ============================================================

WomenHealthCondition = Literal[
    "none",
    "pcos",
    "menstrual_wellness",
    "pregnancy",
    "breastfeeding",
]


# ============================================================
# DYNAMIC ADDITIONAL HEALTH INFORMATION
# ============================================================
#
# Used for health-report values that do not have dedicated
# HealthProfile fields.
#
# Example:
#
# {
#     "name": "Vitamin D",
#     "value": "14",
#     "unit": "ng/mL",
#     "report_flag": "Low"
# }
#
# This structure is dynamic, so we do not need separate
# Pydantic/database fields for every possible laboratory test.
#
# Examples:
# Vitamin D
# Vitamin B12
# Hemoglobin
# Ferritin
# LDL
# HDL
# Creatinine
# TSH
# HbA1c
# etc.
#
class AdditionalHealthItem(BaseModel):
    name: str

    value: Optional[str] = None

    unit: Optional[str] = None

    report_flag: Optional[str] = None


# ============================================================
# CREATE HEALTH PROFILE
# ============================================================

class HealthProfileCreate(BaseModel):
    user_id: int

    systolic_bp: Optional[float] = Field(
        default=None,
        gt=0
    )

    diastolic_bp: Optional[float] = Field(
        default=None,
        gt=0
    )

    blood_sugar_mg_dl: Optional[float] = Field(
        default=None,
        gt=0
    )

    thyroid_status: Optional[str] = None

    activity_level: str

    diet_preference: Optional[str] = None

    # --------------------------------------------------------
    # ADDITIONAL HEALTH INFORMATION
    # --------------------------------------------------------
    #
    # Stored as JSONB in PostgreSQL.
    #
    # Example:
    #
    # [
    #     {
    #         "name": "Vitamin D",
    #         "value": "14",
    #         "unit": "ng/mL",
    #         "report_flag": "Low"
    #     },
    #     {
    #         "name": "Hemoglobin",
    #         "value": "10.8",
    #         "unit": "g/dL",
    #         "report_flag": "Low"
    #     }
    # ]
    #
    additional_health_info: List[
        AdditionalHealthItem
    ] = Field(
        default_factory=list
    )

    # --------------------------------------------------------
    # FOOD REGION
    # --------------------------------------------------------
    #
    # User's state / food region.
    #
    # Used for regional diet personalization.
    #
    # Examples:
    #
    # Andhra Pradesh
    # Telangana
    # Tamil Nadu
    # Kerala
    # Karnataka
    # Maharashtra
    # Punjab
    # Gujarat
    # West Bengal
    #
    food_region: Optional[str] = None

    goal: str

    women_health_condition: Optional[
        WomenHealthCondition
    ] = None


# ============================================================
# HEALTH PROFILE RESPONSE
# ============================================================

class HealthProfileResponse(BaseModel):
    id: int

    user_id: int

    # Calculated automatically from height and weight
    bmi: float

    systolic_bp: Optional[float]

    diastolic_bp: Optional[float]

    blood_sugar_mg_dl: Optional[float]

    thyroid_status: Optional[str]

    activity_level: str

    diet_preference: Optional[str]

    # --------------------------------------------------------
    # ADDITIONAL HEALTH INFORMATION
    # --------------------------------------------------------
    #
    # Latest confirmed dynamic health information.
    #
    additional_health_info: List[
        AdditionalHealthItem
    ] = Field(
        default_factory=list
    )

    # --------------------------------------------------------
    # FOOD REGION
    # --------------------------------------------------------

    food_region: Optional[str]

    goal: str

    women_health_condition: Optional[
        WomenHealthCondition
    ]

    model_config = {
        "from_attributes": True
    }


# ============================================================
# UPDATE USER + HEALTH PROFILE
# ============================================================

class HealthProfileUpdate(BaseModel):
    height_cm: float = Field(gt=0)
    weight_kg: float = Field(gt=0)

    systolic_bp: Optional[float] = Field(
        default=None,
        gt=0
    )

    diastolic_bp: Optional[float] = Field(
        default=None,
        gt=0
    )

    blood_sugar_mg_dl: Optional[float] = Field(
        default=None,
        gt=0
    )

    thyroid_status: Optional[str] = None

    activity_level: str

    diet_preference: Optional[str] = None

    additional_health_info: List[
        AdditionalHealthItem
    ] = Field(default_factory=list)

    food_region: Optional[str] = None

    goal: str

    women_health_condition: Optional[
        WomenHealthCondition
    ] = None
    # --------------------------------------------------------
    # ADDITIONAL HEALTH INFORMATION
    # --------------------------------------------------------
    #
    # Dynamic confirmed health information.
    #
    # When report information is confirmed, the backend can
    # merge new results with the existing JSONB information.
    #
    additional_health_info: List[
        AdditionalHealthItem
    ] = Field(
        default_factory=list
    )

    # --------------------------------------------------------
    # FOOD REGION
    # --------------------------------------------------------

    food_region: Optional[str] = None

    goal: str

    women_health_condition: Optional[
        WomenHealthCondition
    ] = None
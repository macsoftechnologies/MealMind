from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    ForeignKey,
    DateTime,
)

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

from database import Base


class HealthProfile(Base):
    __tablename__ = "health_profiles"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey(
            "users.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        unique=True,
        index=True
    )

    # --------------------------------------------------------
    # BASIC HEALTH INFORMATION
    # --------------------------------------------------------

    bmi = Column(
        Float,
        nullable=False
    )

    systolic_bp = Column(
        Float,
        nullable=True
    )

    diastolic_bp = Column(
        Float,
        nullable=True
    )

    blood_sugar_mg_dl = Column(
        Float,
        nullable=True
    )

    thyroid_status = Column(
        String,
        nullable=True
    )

    # --------------------------------------------------------
    # LIFESTYLE + DIET
    # --------------------------------------------------------

    activity_level = Column(
        String,
        nullable=False
    )

    diet_preference = Column(
        String,
        nullable=True
    )

    # --------------------------------------------------------
    # ADDITIONAL HEALTH INFORMATION
    # --------------------------------------------------------
    #
    # Stores dynamic structured health information extracted
    # from uploaded medical/health reports.
    #
    # We use JSONB because different reports may contain
    # different health measurements.
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
    #     },
    #     {
    #         "name": "Vitamin B12",
    #         "value": "180",
    #         "unit": "pg/mL",
    #         "report_flag": "Low"
    #     }
    # ]
    #
    # The structure is dynamic:
    #
    # - Vitamin D
    # - Vitamin B12
    # - Hemoglobin
    # - Ferritin
    # - Iron
    # - LDL
    # - HDL
    # - Creatinine
    # - TSH
    # - HbA1c
    # - or other useful measured health information
    #
    # We do NOT need separate database columns for every
    # possible laboratory test.
    #
    # Latest confirmed values are stored here.
    #
    # Historical report values remain separately available
    # in the health_reports table.
    #
    # This information can later be used for:
    #
    # - Diet plan generation
    # - Meal analysis
    # - Personalized feedback
    # - Adaptive rest-of-day guidance
    #
    # AI-extracted information should be reviewed and
    # confirmed by the user before updating this field.
    #
    additional_health_info = Column(
        JSONB,
        nullable=False,
        default=list
    )

    # --------------------------------------------------------
    # FOOD REGION
    # --------------------------------------------------------
    #
    # User's state / food region.
    #
    # Examples:
    #
    # Andhra Pradesh
    # Telangana
    # Tamil Nadu
    # Kerala
    # Karnataka
    # Punjab
    # Gujarat
    # Maharashtra
    # West Bengal
    #
    # Used for regional food personalization
    # in diet-plan generation.
    #
    # Nullable so existing users continue working.
    #
    food_region = Column(
        String,
        nullable=True
    )

    # --------------------------------------------------------
    # USER GOAL
    # --------------------------------------------------------

    goal = Column(
        String,
        nullable=False
    )

    # --------------------------------------------------------
    # WOMEN'S HEALTH CONTEXT
    # --------------------------------------------------------
    #
    # Possible values:
    #
    # none
    # pcos
    # menstrual_wellness
    # pregnancy
    # breastfeeding
    #
    # Nullable so existing users continue working.
    #
    women_health_condition = Column(
        String,
        nullable=True
    )

    # --------------------------------------------------------
    # TIMESTAMPS
    # --------------------------------------------------------

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
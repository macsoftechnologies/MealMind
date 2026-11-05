from datetime import date, datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# ============================================================
# ADDITIONAL HEALTH ITEM
# ============================================================

class AdditionalHealthItem(BaseModel):
    name: str

    value: Optional[str] = None

    unit: Optional[str] = None

    # Only a flag explicitly present in the report.
    # Examples:
    # Low
    # High
    # Normal
    # Borderline
    report_flag: Optional[str] = None


# ============================================================
# EXTRACTED HEALTH VALUES
# ============================================================

class ExtractedHealthValues(BaseModel):

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

    additional_health_info: List[
        AdditionalHealthItem
    ] = []


# ============================================================
# REPORT ANALYSIS RESPONSE
# ============================================================

class HealthReportAnalysisResponse(BaseModel):

    original_filename: str

    report_date: Optional[date] = None

    extracted: ExtractedHealthValues

    # Current values are returned so frontend can show:
    #
    # 230 → 300
    #
    current_profile: Dict[str, Any]

    # Explicitly identifies fields whose extracted value
    # differs from the current profile.
    changed_fields: Dict[str, Any]

    message: str = (
        "Review the extracted information before updating "
        "your health profile."
    )


# ============================================================
# CONFIRM REPORT
# ============================================================

class HealthReportConfirmRequest(BaseModel):

    report_date: Optional[date] = None

    original_filename: str

    # Only values confirmed by the user should be sent here.
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

    additional_health_info: List[
        AdditionalHealthItem
    ] = []


# ============================================================
# SAVED REPORT RESPONSE
# ============================================================

class HealthReportResponse(BaseModel):

    id: int
    user_id: int

    original_filename: str

    file_type: Optional[str]

    report_date: Optional[date]

    extracted_data: Optional[Dict[str, Any]]

    additional_health_info: Optional[str]

    created_at: datetime

    model_config = {
        "from_attributes": True
    }
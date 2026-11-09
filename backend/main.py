import time
import os

from datetime import date, datetime, timedelta
from typing import Optional, Any
from pydantic import BaseModel
from io import BytesIO
from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from sqlalchemy.orm import Session

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    KeepTogether,
)

from db_models import diet_plan
from models import user

from models import health_profile
from database import Base, engine, get_db

from db_models.meal import Meal
from db_models.meal_food import MealFood
from db_models.user import User
from db_models.health_profile import HealthProfile
from db_models.health_report import HealthReport
from db_models.diet_plan import DietPlan
from db_models.calendar_event import CalendarEvent
from models.meal import MealAnalysisResponse

from models.user import (
    UserCreate,
    UserResponse,
    UserRegister,
    UserLogin,
)
from models.diet_plan import DietPlanCreate
from models.health_profile import (
    HealthProfileCreate,
    HealthProfileResponse,
    HealthProfileUpdate,
)

from models.health_report import (
    HealthReportConfirmRequest,
)

from services.health_report_service import (
    analyze_health_report,
)

from services.deepseek_service import analyze_meal
from services.calorie_service import calculate_nutrition_targets
from services.diet_plan_service import (
    generate_diet_plan,
    generate_weekly_diet_plan,
    get_week_dates,
)
from services.auth_service import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
)

from datetime import (
    datetime,
    timedelta,
    timezone,
)

from db_models.password_reset_otp import (
    PasswordResetOTP,
)

from models.user import (
    ForgotPasswordRequest,
    VerifyResetOTPRequest,
    ResetPasswordRequest,
    ChangePasswordRequest,
)

from services.password_reset_service import (
    generate_otp,
    hash_otp,
    verify_otp,
)

from services.email_service import (
    send_password_reset_otp,
)


# ============================================================
# CREATE DATABASE TABLES
# ============================================================

Base.metadata.create_all(bind=engine)


# ============================================================
# CREATE FASTAPI APP
# ============================================================

app = FastAPI(
    title="AI Dietplan Assistant API",
    version="1.0.0"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ] + ([os.getenv("FRONTEND_URL")] if os.getenv("FRONTEND_URL") else []),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():
    return {
        "message": "AI Dietplan Assistant API is running"
    }


# ============================================================
# REGISTER USER
# ============================================================

@app.post("/auth/register")
def register_user(
    request: UserRegister,
    db: Session = Depends(get_db)
):
    normalized_email = (
        request.email
        .lower()
        .strip()
    )

    existing_user = (
        db.query(User)
        .filter(User.email == normalized_email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="An account with this email already exists"
        )

    user = User(
        name=request.name.strip(),
        email=normalized_email,
        password_hash=hash_password(
            request.password
        ),
        age=request.age,
        gender=request.gender,
        height_cm=request.height_cm,
        weight_kg=request.weight_kg
    )

    try:
        db.add(user)
        db.commit()
        db.refresh(user)

    except Exception:
        db.rollback()
        raise

    access_token = create_access_token(
        user_id=user.id,
        email=user.email
    )

    return {
        "message": "Account created successfully",
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "age": user.age,
            "gender": user.gender,
            "height_cm": user.height_cm,
            "weight_kg": user.weight_kg
        }
    }


# ============================================================
# LOGIN USER
# ============================================================

@app.post("/auth/login")
def login_user(
    request: UserLogin,
    db: Session = Depends(get_db)
):
    normalized_email = (
        request.email
        .lower()
        .strip()
    )

    user = (
        db.query(User)
        .filter(User.email == normalized_email)
        .first()
    )

    if (
        not user
        or not user.password_hash
        or not verify_password(
            request.password,
            user.password_hash
        )
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    access_token = create_access_token(
        user_id=user.id,
        email=user.email
    )

    return {
        "message": "Login successful",
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email
        }
    }


# ============================================================
# GET CURRENT AUTHENTICATED USER
# ============================================================

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials

    payload = decode_access_token(token)

    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    user_id = payload.get("sub")

    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication token"
        )

    try:
        user_id = int(user_id)

    except (TypeError, ValueError):
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication token"
        )

    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="User not found"
        )

    return user


@app.get("/auth/me")
def get_authenticated_user(
    current_user: User = Depends(get_current_user)
):
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "age": current_user.age,
        "gender": current_user.gender,
        "height_cm": current_user.height_cm,
        "weight_kg": current_user.weight_kg
    }


# ============================================================
# CREATE USER
# ============================================================

@app.post(
    "/users",
    response_model=UserResponse
)
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    user = User(
        name=user_data.name,
        age=user_data.age,
        gender=user_data.gender,
        height_cm=user_data.height_cm,
        weight_kg=user_data.weight_kg
    )

    try:
        db.add(user)
        db.commit()
        db.refresh(user)

    except Exception:
        db.rollback()
        raise

    return user


# ============================================================
# CREATE HEALTH PROFILE
# ============================================================

@app.post(
    "/health-profile",
    response_model=HealthProfileResponse
)
def create_health_profile(
    health_data: HealthProfileCreate,
    db: Session = Depends(get_db)
):
    user = (
        db.query(User)
        .filter(User.id == health_data.user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    existing_profile = (
        db.query(HealthProfile)
        .filter(HealthProfile.user_id == health_data.user_id)
        .first()
    )

    if existing_profile:
        raise HTTPException(
            status_code=400,
            detail="Health profile already exists for this user"
        )

    height_m = user.height_cm / 100
    bmi = round(user.weight_kg / (height_m ** 2), 2)

    women_health_condition = None
    if user.gender.lower().strip() == "female":
        women_health_condition = (
            health_data.women_health_condition or "none"
        )

    health_profile = HealthProfile(
        user_id=health_data.user_id,
        bmi=bmi,
        systolic_bp=health_data.systolic_bp,
        diastolic_bp=health_data.diastolic_bp,
        blood_sugar_mg_dl=health_data.blood_sugar_mg_dl,
        thyroid_status=health_data.thyroid_status,
        activity_level=health_data.activity_level,
        diet_preference=health_data.diet_preference,
        additional_health_info=[
            item.model_dump()
            for item in health_data.additional_health_info
        ],
        food_region=health_data.food_region,
        goal=health_data.goal,
        women_health_condition=women_health_condition
    )

    try:
        db.add(health_profile)
        db.commit()
        db.refresh(health_profile)
    except Exception:
        db.rollback()
        raise

    return health_profile


# ============================================================
# GET USER + HEALTH PROFILE
# ============================================================

@app.get("/users/{user_id}/profile")
def get_user_profile(
    user_id: int,
    db: Session = Depends(get_db)
):
    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    health_profile = (
        db.query(HealthProfile)
        .filter(HealthProfile.user_id == user_id)
        .first()
    )

    return {
        "user": {
            "id": user.id,
            "name": user.name,
            "age": user.age,
            "gender": user.gender,
            "height_cm": user.height_cm,
            "weight_kg": user.weight_kg
        },
        "health_profile": {
            "bmi": health_profile.bmi,
            "systolic_bp": health_profile.systolic_bp,
            "diastolic_bp": health_profile.diastolic_bp,
            "blood_sugar_mg_dl": health_profile.blood_sugar_mg_dl,
            "thyroid_status": health_profile.thyroid_status,
            "activity_level": health_profile.activity_level,
            "diet_preference": health_profile.diet_preference,
            "additional_health_info": (
                health_profile.additional_health_info or []
            ),
            "food_region": health_profile.food_region,
            "goal": health_profile.goal,
            "women_health_condition": (
                health_profile.women_health_condition
            )
        } if health_profile else None
    }


# ============================================================
# UPDATE USER + HEALTH PROFILE
# ============================================================

@app.put("/users/{user_id}/profile")
def update_user_profile(
    user_id: int,
    request: HealthProfileUpdate,
    db: Session = Depends(get_db),
):
    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    health_profile = (
        db.query(HealthProfile)
        .filter(HealthProfile.user_id == user_id)
        .first()
    )

    if not health_profile:
        raise HTTPException(
            status_code=404,
            detail="Health profile not found",
        )

    
    user.height_cm = request.height_cm
    user.weight_kg = request.weight_kg

    height_m = request.height_cm / 100
    bmi = request.weight_kg / (height_m ** 2)

    health_profile.bmi = round(bmi, 2)
    health_profile.systolic_bp = request.systolic_bp
    health_profile.diastolic_bp = request.diastolic_bp
    health_profile.blood_sugar_mg_dl = request.blood_sugar_mg_dl
    health_profile.thyroid_status = request.thyroid_status
    health_profile.activity_level = request.activity_level
    health_profile.diet_preference = request.diet_preference
    health_profile.additional_health_info = [
        item.model_dump()
        for item in request.additional_health_info
    ]
    health_profile.food_region = request.food_region
    health_profile.goal = request.goal

    if user.gender.lower().strip() == "female":
            health_profile.women_health_condition = (
        request.women_health_condition or "none"
    )
    else:
            health_profile.women_health_condition = None
    try:
        db.commit()
        db.refresh(user)
        db.refresh(health_profile)
    except Exception:
        db.rollback()
        raise

    return {
        "message": "Profile updated successfully",
        "user": {
            "id": user.id,
            "name": user.name,
            "age": user.age,
            "gender": user.gender,
            "height_cm": user.height_cm,
            "weight_kg": user.weight_kg,
        },
        "health_profile": {
            "id": health_profile.id,
            "user_id": health_profile.user_id,
            "bmi": health_profile.bmi,
            "systolic_bp": health_profile.systolic_bp,
            "diastolic_bp": health_profile.diastolic_bp,
            "blood_sugar_mg_dl": health_profile.blood_sugar_mg_dl,
            "thyroid_status": health_profile.thyroid_status,
            "activity_level": health_profile.activity_level,
            "diet_preference": health_profile.diet_preference,
            "additional_health_info": (
                health_profile.additional_health_info or []
            ),
            "food_region": health_profile.food_region,
            "goal": health_profile.goal,
            "women_health_condition": (
                health_profile.women_health_condition
            ),
        },
    }


# ============================================================
# ANALYZE HEALTH REPORT
# ============================================================

@app.post("/health-report/analyze")
async def analyze_health_report_endpoint(
    report: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    health_profile = (
        db.query(HealthProfile)
        .filter(HealthProfile.user_id == current_user.id)
        .first()
    )

    if not health_profile:
        raise HTTPException(
            status_code=404,
            detail="Health profile not found"
        )

    allowed_types = {
        "application/pdf",
        "image/jpeg",
        "image/jpg",
        "image/png",
        "image/webp",
    }

    if report.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported file type. "
                "Upload PDF, JPG, JPEG, PNG or WEBP."
            )
        )

    report_bytes = await report.read()

    if not report_bytes:
        raise HTTPException(
            status_code=400,
            detail="Uploaded health report is empty"
        )

    max_file_size = 10 * 1024 * 1024
    if len(report_bytes) > max_file_size:
        raise HTTPException(
            status_code=400,
            detail="Health report must be 10 MB or smaller"
        )

    try:
        extracted = analyze_health_report(
            file_bytes=report_bytes,
            content_type=report.content_type
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Health report analysis failed: {str(e)}"
        )

    current_profile = {
        "systolic_bp": health_profile.systolic_bp,
        "diastolic_bp": health_profile.diastolic_bp,
        "blood_sugar_mg_dl": health_profile.blood_sugar_mg_dl,
        "thyroid_status": health_profile.thyroid_status,
        "additional_health_info": (
            health_profile.additional_health_info or []
        ),
    }

    changed_fields = {}

    comparable_fields = [
        "systolic_bp",
        "diastolic_bp",
        "blood_sugar_mg_dl",
        "thyroid_status",
    ]

    for field_name in comparable_fields:
        new_value = extracted.get(field_name)
        if new_value is None:
            continue

        old_value = current_profile.get(field_name)
        if old_value != new_value:
            changed_fields[field_name] = {
                "old_value": old_value,
                "new_value": new_value,
            }

    existing_additional = {
        str(item.get("name", "")).strip().lower(): item
        for item in (health_profile.additional_health_info or [])
        if isinstance(item, dict) and item.get("name")
    }

    additional_changes = []

    for item in extracted.get("additional_health_info", []):
        if not isinstance(item, dict):
            continue

        name = str(item.get("name", "")).strip()
        if not name:
            continue

        old_item = existing_additional.get(name.lower())
        if old_item != item:
            additional_changes.append({
                "name": name,
                "old_value": old_item,
                "new_value": item,
            })

    if additional_changes:
        changed_fields["additional_health_info"] = additional_changes

    return {
        "original_filename": report.filename,
        "file_type": report.content_type,
        "report_date": extracted.get("report_date"),
        "extracted": extracted,
        "current_profile": current_profile,
        "changed_fields": changed_fields,
        "message": (
            "Review the extracted information before "
            "updating your health profile."
        )
    }


# ============================================================
# MERGE DYNAMIC ADDITIONAL HEALTH INFORMATION
# ============================================================

def merge_additional_health_info(
    existing_items,
    new_items
):
    """
    Keep existing confirmed tests when a new report does not
    contain them. When the same test appears again, the newest
    confirmed result becomes the active value.
    """

    merged = {}

    for item in existing_items or []:
        if not isinstance(item, dict):
            continue

        name = str(item.get("name", "")).strip()
        if not name:
            continue

        merged[name.lower()] = {
            "name": name,
            "value": item.get("value"),
            "unit": item.get("unit"),
            "report_flag": item.get("report_flag"),
        }

    for item in new_items or []:
        name = str(item.name).strip()
        if not name:
            continue

        merged[name.lower()] = {
            "name": name,
            "value": item.value,
            "unit": item.unit,
            "report_flag": item.report_flag,
        }

    return list(merged.values())


# ============================================================
# CONFIRM HEALTH REPORT
# ============================================================

@app.post("/health-report/confirm")
def confirm_health_report(
    request: HealthReportConfirmRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    health_profile = (
        db.query(HealthProfile)
        .filter(HealthProfile.user_id == current_user.id)
        .first()
    )

    if not health_profile:
        raise HTTPException(
            status_code=404,
            detail="Health profile not found"
        )

    if request.systolic_bp is not None:
        health_profile.systolic_bp = request.systolic_bp

    if request.diastolic_bp is not None:
        health_profile.diastolic_bp = request.diastolic_bp

    if request.blood_sugar_mg_dl is not None:
        health_profile.blood_sugar_mg_dl = (
            request.blood_sugar_mg_dl
        )

    if request.thyroid_status is not None:
        cleaned_thyroid = request.thyroid_status.strip()
        if cleaned_thyroid:
            health_profile.thyroid_status = cleaned_thyroid

    if request.additional_health_info:
        health_profile.additional_health_info = (
            merge_additional_health_info(
                existing_items=(
                    health_profile.additional_health_info or []
                ),
                new_items=request.additional_health_info
            )
        )

    extracted_data = {
        "systolic_bp": request.systolic_bp,
        "diastolic_bp": request.diastolic_bp,
        "blood_sugar_mg_dl": request.blood_sugar_mg_dl,
        "thyroid_status": request.thyroid_status,
        "additional_health_info": [
            item.model_dump()
            for item in request.additional_health_info
        ],
    }

    # The complete structured report history is stored in
    # extracted_data JSONB. The original medical file is not
    # permanently retained in V1.
    report_record = HealthReport(
        user_id=current_user.id,
        original_filename=request.original_filename,
        file_path=None,
        file_type=None,
        report_date=request.report_date,
        extracted_data=extracted_data,
        additional_health_info=None,
    )

    try:
        db.add(report_record)
        db.flush()

        reports = (
            db.query(HealthReport)
            .filter(HealthReport.user_id == current_user.id)
            .order_by(
                HealthReport.created_at.desc(),
                HealthReport.id.desc(),
            )
            .all()
        )

        for old_report in reports[10:]:
            db.delete(old_report)

        db.commit()
        db.refresh(health_profile)
        db.refresh(report_record)

    except Exception:
        db.rollback()
        raise

    return {
        "message": "Health report confirmed and profile updated",
        "report_id": report_record.id,
        "health_profile": {
            "systolic_bp": health_profile.systolic_bp,
            "diastolic_bp": health_profile.diastolic_bp,
            "blood_sugar_mg_dl": health_profile.blood_sugar_mg_dl,
            "thyroid_status": health_profile.thyroid_status,
            "additional_health_info": (
                health_profile.additional_health_info or []
            ),
        }
    }


# ============================================================
# GET HEALTH REPORT HISTORY
# ============================================================

@app.get("/health-reports")
def get_health_reports(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    reports = (
        db.query(HealthReport)
        .filter(HealthReport.user_id == current_user.id)
        .order_by(
            HealthReport.created_at.desc(),
            HealthReport.id.desc(),
        )
        .all()
    )

    result = []

    for report in reports:
        result.append({
            "id": report.id,
            "original_filename": report.original_filename,
            "report_date": (
                report.report_date.isoformat()
                if report.report_date
                else None
            ),
            "extracted_data": report.extracted_data,
            "additional_health_info": (
                (report.extracted_data or {}).get(
                    "additional_health_info",
                    []
                )
            ),
            "created_at": report.created_at,
        })

    return {
        "count": len(result),
        "maximum_reports": 10,
        "reports": result,
    }


# ============================================================
# DELETE HEALTH REPORT HISTORY RECORD
# ============================================================

@app.delete("/health-reports/{report_id}")
def delete_health_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    report = (
        db.query(HealthReport)
        .filter(
            HealthReport.id == report_id,
            HealthReport.user_id == current_user.id,
        )
        .first()
    )

    if not report:
        raise HTTPException(
            status_code=404,
            detail="Health report not found"
        )

    try:
        db.delete(report)
        db.commit()
    except Exception:
        db.rollback()
        raise

    return {
        "message": "Health report deleted successfully",
        "report_id": report_id,
    }


# ============================================================
# TODAY'S NUTRITION CONTEXT FOR ADAPTIVE MEAL GUIDANCE
# ============================================================

def get_today_nutrition_context(
    db: Session,
    user_id: int,
):
    """
    Collect nutrition already consumed today together with the
    user's latest daily diet-plan targets.

    IMPORTANT:
    The newly uploaded meal is NOT included here because this
    function is called before the current meal is analyzed
    and saved.

    This function does NOT call DeepSeek.
    """

    # --------------------------------------------------------
    # CURRENT LOCAL DAY
    # --------------------------------------------------------

    today = date.today()

    start_of_day = datetime.combine(
        today,
        datetime.min.time()
    )

    start_of_next_day = (
        start_of_day
        + timedelta(days=1)
    )


    # --------------------------------------------------------
    # GET MEALS ALREADY ANALYZED TODAY
    # --------------------------------------------------------

    today_meals = (
        db.query(Meal)
        .filter(
            Meal.user_id == user_id,
            Meal.created_at >= start_of_day,
            Meal.created_at < start_of_next_day,
        )
        .all()
    )


    # --------------------------------------------------------
    # NUTRITION CONSUMED BEFORE CURRENT MEAL
    # --------------------------------------------------------

    consumed_before_meal = {
        "calories": round(
            sum(
                float(
                    meal.total_calories
                    or 0
                )
                for meal in today_meals
            ),
            1
        ),

        "protein_g": round(
            sum(
                float(
                    meal.total_protein_g
                    or 0
                )
                for meal in today_meals
            ),
            1
        ),

        "carbohydrates_g": round(
            sum(
                float(
                    meal.total_carbohydrates_g
                    or 0
                )
                for meal in today_meals
            ),
            1
        ),

        "fat_g": round(
            sum(
                float(
                    meal.total_fat_g
                    or 0
                )
                for meal in today_meals
            ),
            1
        ),

        "fiber_g": round(
            sum(
                float(
                    meal.total_fiber_g
                    or 0
                )
                for meal in today_meals
            ),
            1
        ),
    }
        # --------------------------------------------------------
    # GET LATEST SAVED DIET PLAN
    # --------------------------------------------------------

    diet_plan = (
        db.query(DietPlan)
        .filter(DietPlan.user_id == user_id)
        .order_by(DietPlan.created_at.desc())
        .first()
    )

    # Meal analysis must still work even if the user
    # has not generated a diet plan yet.
    if not diet_plan:
        return {
            "available": False,
            "consumed_before_meal": consumed_before_meal,
            "targets": None,
            "planned_meals": [],
        }

    # --------------------------------------------------------
    # DAILY NUTRITION TARGETS
    # --------------------------------------------------------

    targets = {
        "calories": float(
            diet_plan.target_calories or 0
        ),

        "protein_g": float(
            diet_plan.target_protein_g or 0
        ),

        "carbohydrates_g": float(
            diet_plan.target_carbohydrates_g or 0
        ),

        "fat_g": float(
            diet_plan.target_fat_g or 0
        ),

        "fiber_g": float(
            diet_plan.target_fiber_g or 0
        ),
    }

    # --------------------------------------------------------
    # TODAY'S PLANNED MEALS
    # --------------------------------------------------------

    planned_meals = []

    today_iso = today.isoformat()

    # --------------------------------------------------------
    # FIRST TRY THE NEW WEEKLY PLAN
    # --------------------------------------------------------

    if isinstance(
        diet_plan.weekly_plan,
        dict
    ):
        weekly_days = diet_plan.weekly_plan.get(
            "days",
            []
        )

        for day_plan in weekly_days:

            if (
                day_plan.get("date")
                == today_iso
            ):
                planned_meals = day_plan.get(
                    "meals",
                    []
                )

                break


    # --------------------------------------------------------
    # FALLBACK TO OLD ONE-DAY PLAN
    # --------------------------------------------------------

    if not planned_meals:

        planned_meals = (
            diet_plan.meals
            if isinstance(
                diet_plan.meals,
                list
            )
            else []
        )


    # --------------------------------------------------------
    # RETURN TODAY'S NUTRITION CONTEXT
    # --------------------------------------------------------
    return {
        "available": True,

        "consumed_before_meal":
            consumed_before_meal,

        "targets":
            targets,

        "planned_meals":
            planned_meals,
    }
# ============================================================
# SAVE MEAL REQUEST
# ============================================================

class SaveMealRequest(BaseModel):
    image_filename: Optional[str] = None
    user_comment: Optional[str] = None
    analysis: dict[str, Any]
# ============================================================
# ANALYZE MEAL
# ============================================================

@app.post(
    "/analyze-meal",
    response_model=MealAnalysisResponse
)
async def analyze_meal_endpoint(
    user_id: int,
    image: UploadFile = File(...),
    comment: str | None = Form(None),
    db: Session = Depends(get_db)
):
    # --------------------------------------------------------
    # FIND USER
    # --------------------------------------------------------

    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # --------------------------------------------------------
    # FIND HEALTH PROFILE
    # --------------------------------------------------------

    health_profile = (
        db.query(HealthProfile)
        .filter(
            HealthProfile.user_id == user_id
        )
        .first()
    )

    if not health_profile:
        raise HTTPException(
            status_code=400,
            detail="Health profile not found for this user"
        )

    # --------------------------------------------------------
    # CLEAN OPTIONAL USER MEAL CONTEXT
    # --------------------------------------------------------

    user_comment = (
        comment.strip()
        if comment and comment.strip()
        else None
    )

    # --------------------------------------------------------
    # GET TODAY'S NUTRITION CONTEXT
    #
    # IMPORTANT:
    # This happens BEFORE the current meal is analyzed/saved.
    # Therefore the current meal is not double-counted.
    # --------------------------------------------------------

    daily_nutrition_context = get_today_nutrition_context(
        db=db,
        user_id=user_id
    )

    # --------------------------------------------------------
    # READ IMAGE
    # --------------------------------------------------------

    image_bytes = await image.read()

    if not image_bytes:
        raise HTTPException(
            status_code=400,
            detail="Uploaded image is empty"
        )

    # --------------------------------------------------------
    # START TIMER
    # --------------------------------------------------------

    start_time = time.perf_counter()

    # --------------------------------------------------------
    # DEEPSEEK MEAL ANALYSIS
    #
    # IMPORTANT:
    # There is only ONE DeepSeek call here.
    #
    # The same call receives:
    # - current meal image
    # - optional user comment
    # - user information
    # - health profile
    # - nutrition already consumed today
    # - daily nutrition targets
    # - original one-day planned meals
    #
    # DeepSeek can therefore return:
    # - meal nutrition
    # - personalized feedback
    # - rest_of_day_advice
    # --------------------------------------------------------

    try:
        result = analyze_meal(
            image_bytes=image_bytes,
            mime_type=image.content_type,
            user=user,
            health_profile=health_profile,
            user_comment=user_comment,
            daily_nutrition_context=daily_nutrition_context
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Meal analysis failed: {str(e)}"
        )

        # --------------------------------------------------------
    # PROCESSING TIME
    # --------------------------------------------------------

    processing_time = (
        time.perf_counter() - start_time
    )

    result["processing_time_seconds"] = round(
        processing_time,
        2
    )

    # --------------------------------------------------------
    # PREVIEW INFORMATION
    # --------------------------------------------------------

    result["image_filename"] = image.filename
    result["user_comment"] = user_comment

    return result

# ============================================================
# SAVE ANALYZED MEAL
# ============================================================

@app.post("/users/{user_id}/meals/save")
def save_analyzed_meal(
    user_id: int,
    request: SaveMealRequest,
    db: Session = Depends(get_db)
):
    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    result = request.analysis
    meal_total = result.get("meal_total", {})
    foods = result.get("foods", [])

    try:
        meal = Meal(
            user_id=user_id,
            image_filename=request.image_filename,
            user_comment=request.user_comment,

            total_calories=meal_total["calories"],
            total_protein_g=meal_total["protein_g"],
            total_carbohydrates_g=
                meal_total["carbohydrates_g"],
            total_fat_g=meal_total["fat_g"],
            total_fiber_g=meal_total["fiber_g"],

            personalized_feedback=
                result.get(
                    "personalized_feedback",
                    {}
                ),

            processing_time_seconds=
                result.get(
                    "processing_time_seconds"
                )
        )

        db.add(meal)
        db.flush()

        for food in foods:
            meal_food = MealFood(
                meal_id=meal.id,

                food_name=
                    food.get("food_name"),

                approximate_portion=
                    food.get(
                        "approximate_portion"
                    ),

                approximate_percentage=
                    food.get(
                        "approximate_percentage_of_visible_meal"
                    ),

                calories=
                    food.get("calories", 0),

                protein_g=
                    food.get("protein_g", 0),

                carbohydrates_g=
                    food.get(
                        "carbohydrates_g",
                        0
                    ),

                fat_g=
                    food.get("fat_g", 0),

                fiber_g=
                    food.get("fiber_g", 0),

                confidence_score=
                    food.get(
                        "confidence_score"
                    )
            )

            db.add(meal_food)

        db.commit()
        db.refresh(meal)

    except Exception:
        db.rollback()
        raise

    return {
        "message": "Meal saved successfully",
        "meal_id": meal.id
    }

# ============================================================
# GET USER MEAL HISTORY
#
# GET /users/2/meals
# -> returns all meals
#
# GET /users/2/meals?date=2026-10-12
# -> returns meals for selected date
# ============================================================

@app.get("/users/{user_id}/meals")
def get_user_meals(
    user_id: int,
    date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    query = (
        db.query(Meal)
        .filter(Meal.user_id == user_id)
    )

    if date is not None:
        start_of_day = datetime.combine(
            date,
            datetime.min.time()
        )

        start_of_next_day = (
            start_of_day + timedelta(days=1)
        )

        query = query.filter(
            Meal.created_at >= start_of_day,
            Meal.created_at < start_of_next_day
        )

    meals = (
        query
        .order_by(Meal.created_at.desc())
        .all()
    )

    result = []

    for meal in meals:
        foods = (
            db.query(MealFood)
            .filter(MealFood.meal_id == meal.id)
            .all()
        )

        result.append({
            "meal_id":
                meal.id,

            "image_filename":
                meal.image_filename,

            "meal_total": {
                "calories":
                    meal.total_calories,

                "protein_g":
                    meal.total_protein_g,

                "carbohydrates_g":
                    meal.total_carbohydrates_g,

                "fat_g":
                    meal.total_fat_g,

                "fiber_g":
                    meal.total_fiber_g
            },

            "foods": [
                {
                    "food_name":
                        food.food_name,

                    "approximate_portion":
                        food.approximate_portion,

                    "approximate_percentage":
                        food.approximate_percentage,

                    "calories":
                        food.calories,

                    "protein_g":
                        food.protein_g,

                    "carbohydrates_g":
                        food.carbohydrates_g,

                    "fat_g":
                        food.fat_g,

                    "fiber_g":
                        food.fiber_g,

                    "confidence_score":
                        food.confidence_score
                }

                for food in foods
            ],

            "personalized_feedback":
                meal.personalized_feedback,

            "processing_time_seconds":
                meal.processing_time_seconds,

            "created_at":
                meal.created_at
        })

    return {
        "user_id": user_id,

        "date": (
            date.isoformat()
            if date is not None
            else None
        ),

        "total_meals": len(result),

        "meals": result
    }


# ============================================================
# DELETE SAVED MEAL
# ============================================================

@app.delete("/users/{user_id}/meals/{meal_id}")
def delete_user_meal(
    user_id: int,
    meal_id: int,
    db: Session = Depends(get_db)
):
    meal = (
        db.query(Meal)
        .filter(
            Meal.id == meal_id,
            Meal.user_id == user_id
        )
        .first()
    )

    if not meal:
        raise HTTPException(
            status_code=404,
            detail="Meal not found"
        )

    try:
        (
            db.query(MealFood)
            .filter(MealFood.meal_id == meal_id)
            .delete(synchronize_session=False)
        )

        db.delete(meal)

        db.commit()

    except Exception:
        db.rollback()
        raise

    return {
        "message": "Meal deleted successfully",
        "meal_id": meal_id
    }


# ============================================================
# GENERATE AND SAVE DIET PLAN
# ============================================================

@app.post("/users/{user_id}/diet-plan")
def create_diet_plan(
    user_id: int,
    request: DietPlanCreate,
    db: Session = Depends(get_db)
):
    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    health_profile = (
        db.query(HealthProfile)
        .filter(HealthProfile.user_id == user_id)
        .first()
    )

    if not health_profile:
        raise HTTPException(
            status_code=404,
            detail="Health profile not found"
        )

    nutrition_targets = calculate_nutrition_targets(
        age=user.age,
        gender=user.gender,
        height_cm=user.height_cm,
        weight_kg=user.weight_kg,
        activity_level=health_profile.activity_level,
        goal=health_profile.goal,
        women_health_condition=(
            health_profile.women_health_condition
        ),
    )

    try:
        generated_plan = generate_diet_plan(
            user=user,
            health_profile=health_profile,
            nutrition_targets=nutrition_targets,
            food_allergies=request.food_allergies,
            foods_to_avoid=request.foods_to_avoid,
            meals_per_day=request.meals_per_day
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Diet plan generation failed: {str(e)}"
        )

    diet_plan = DietPlan(
        user_id=user_id,

        food_allergies=request.food_allergies,
        foods_to_avoid=request.foods_to_avoid,
        meals_per_day=request.meals_per_day,

        bmr=nutrition_targets["bmr"],
        tdee=nutrition_targets["tdee"],

        target_calories=
            nutrition_targets["target_calories"],

        target_protein_g=
            nutrition_targets["protein_g"],

        target_carbohydrates_g=
            nutrition_targets["carbohydrates_g"],

        target_fat_g=
            nutrition_targets["fat_g"],
                    target_fiber_g=
            nutrition_targets["fiber_g"],

        meals=generated_plan["meals"],

        daily_tip=
            generated_plan.get("daily_tip")
    )

    try:
        db.add(diet_plan)
        db.commit()
        db.refresh(diet_plan)

    except Exception:
        db.rollback()
        raise

    return {
        "diet_plan_id":
            diet_plan.id,

        "user_id":
            user_id,

        "goal":
            health_profile.goal,

        "diet_preference":
            health_profile.diet_preference,

        "women_health_condition":
            health_profile.women_health_condition,

        "food_allergies":
            diet_plan.food_allergies,

        "foods_to_avoid":
            diet_plan.foods_to_avoid,

        "meals_per_day":
            diet_plan.meals_per_day,

        "nutrition_targets": {
            "bmr":
                diet_plan.bmr,

            "tdee":
                diet_plan.tdee,

            "target_calories":
                diet_plan.target_calories,

            "protein_g":
                diet_plan.target_protein_g,

            "carbohydrates_g":
                diet_plan.target_carbohydrates_g,

            "fat_g":
                diet_plan.target_fat_g,

            "fiber_g":
                diet_plan.target_fiber_g
        },

        "meals":
            diet_plan.meals,

        "daily_tip":
            diet_plan.daily_tip,

        "created_at":
            diet_plan.created_at
    }

# ============================================================
# GENERATE AND SAVE WEEKLY DIET PLAN
# ============================================================

@app.post("/users/{user_id}/diet-plan/weekly")
def create_weekly_diet_plan(
    user_id: int,
    request: DietPlanCreate,
    db: Session = Depends(get_db)
):
    # --------------------------------------------------------
    # FIND USER
    # --------------------------------------------------------

    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # --------------------------------------------------------
    # FIND HEALTH PROFILE
    # --------------------------------------------------------

    health_profile = (
        db.query(HealthProfile)
        .filter(
            HealthProfile.user_id == user_id
        )
        .first()
    )

    if not health_profile:
        raise HTTPException(
            status_code=404,
            detail="Health profile not found"
        )

    # --------------------------------------------------------
    # CALCULATE DAILY NUTRITION TARGETS
    # --------------------------------------------------------

    nutrition_targets = calculate_nutrition_targets(
        age=user.age,
        gender=user.gender,
        height_cm=user.height_cm,
        weight_kg=user.weight_kg,
        activity_level=health_profile.activity_level,
        goal=health_profile.goal,
        women_health_condition=(
            health_profile.women_health_condition
        ),
    )

    # --------------------------------------------------------
    # GET WEEK DATES
    # --------------------------------------------------------

    week_start, week_end = get_week_dates()

    # --------------------------------------------------------
    # CHECK IF THIS WEEK ALREADY HAS A PLAN
    # --------------------------------------------------------

    existing_plan = (
        db.query(DietPlan)
        .filter(
            DietPlan.user_id == user_id,
            DietPlan.week_start_date == week_start,
        )
        .order_by(
            DietPlan.created_at.desc()
        )
        .first()
    )

    # --------------------------------------------------------
    # GENERATE WEEKLY PLAN USING DEEPSEEK
    # --------------------------------------------------------

    try:
        generated_plan = generate_weekly_diet_plan(
            user=user,
            health_profile=health_profile,
            nutrition_targets=nutrition_targets,
            food_allergies=request.food_allergies,
            foods_to_avoid=request.foods_to_avoid,
            meals_per_day=request.meals_per_day
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=(
                "Weekly diet plan generation failed: "
                f"{str(e)}"
            )
        )

    # --------------------------------------------------------
    # SAVE / REPLACE CURRENT WEEK PLAN
    # --------------------------------------------------------

    if existing_plan:
        diet_plan = existing_plan

        diet_plan.food_allergies = (
            request.food_allergies
        )

        diet_plan.foods_to_avoid = (
            request.foods_to_avoid
        )

        diet_plan.meals_per_day = (
            request.meals_per_day
        )

        diet_plan.bmr = nutrition_targets["bmr"]

        diet_plan.tdee = nutrition_targets["tdee"]

        diet_plan.target_calories = (
            nutrition_targets["target_calories"]
        )

        diet_plan.target_protein_g = (
            nutrition_targets["protein_g"]
        )

        diet_plan.target_carbohydrates_g = (
            nutrition_targets["carbohydrates_g"]
        )

        diet_plan.target_fat_g = (
            nutrition_targets["fat_g"]
        )

        diet_plan.target_fiber_g = (
            nutrition_targets["fiber_g"]
        )

        diet_plan.week_start_date = week_start
        diet_plan.week_end_date = week_end

        diet_plan.weekly_plan = generated_plan

    else:
        diet_plan = DietPlan(
            user_id=user_id,

            food_allergies=request.food_allergies,
            foods_to_avoid=request.foods_to_avoid,
            meals_per_day=request.meals_per_day,

            bmr=nutrition_targets["bmr"],
            tdee=nutrition_targets["tdee"],

            target_calories=(
                nutrition_targets["target_calories"]
            ),

            target_protein_g=(
                nutrition_targets["protein_g"]
            ),

            target_carbohydrates_g=(
                nutrition_targets["carbohydrates_g"]
            ),

            target_fat_g=(
                nutrition_targets["fat_g"]
            ),

            target_fiber_g=(
                nutrition_targets["fiber_g"]
            ),

            week_start_date=week_start,
            week_end_date=week_end,

            weekly_plan=generated_plan,

            # Keep old one-day fields compatible.
            meals=[],
            daily_tip=None
        )

        db.add(diet_plan)

    # --------------------------------------------------------
    # SAVE DATABASE
    # --------------------------------------------------------

    try:
        db.commit()
        db.refresh(diet_plan)

    except Exception:
        db.rollback()
        raise

    # --------------------------------------------------------
    # RESPONSE
    # --------------------------------------------------------

    return {
        "message": (
            "Weekly diet plan generated successfully"
        ),

        "diet_plan_id": diet_plan.id,

        "user_id": user_id,

        "week_start_date": (
            diet_plan.week_start_date.isoformat()
        ),

        "week_end_date": (
            diet_plan.week_end_date.isoformat()
        ),

        "goal": health_profile.goal,

        "diet_preference": (
            health_profile.diet_preference
        ),

        "meals_per_day": (
            diet_plan.meals_per_day
        ),

        "nutrition_targets": {
            "bmr": diet_plan.bmr,
            "tdee": diet_plan.tdee,

            "target_calories": (
                diet_plan.target_calories
            ),

            "protein_g": (
                diet_plan.target_protein_g
            ),

            "carbohydrates_g": (
                diet_plan.target_carbohydrates_g
            ),

            "fat_g": (
                diet_plan.target_fat_g
            ),

            "fiber_g": (
                diet_plan.target_fiber_g
            ),
        },

        "weekly_plan": (
            diet_plan.weekly_plan
        ),

        "created_at": (
            diet_plan.created_at
        ),
    }
    
# ============================================================
# GET CURRENT WEEKLY DIET PLAN
# ============================================================

@app.get("/users/{user_id}/diet-plan/weekly")
def get_weekly_diet_plan(
    user_id: int,
    db: Session = Depends(get_db)
):
    week_start, week_end = get_week_dates()

    diet_plan = (
        db.query(DietPlan)
        .filter(
            DietPlan.user_id == user_id,
            DietPlan.week_start_date == week_start,
        )
        .order_by(
            DietPlan.created_at.desc()
        )
        .first()
    )

    if not diet_plan:
        raise HTTPException(
            status_code=404,
            detail=(
                "No weekly diet plan found "
                "for the current week"
            )
        )

    return {
        "diet_plan_id": diet_plan.id,

        "user_id": diet_plan.user_id,

        "week_start_date": (
            diet_plan.week_start_date.isoformat()
        ),

        "week_end_date": (
            diet_plan.week_end_date.isoformat()
        ),

        "nutrition_targets": {
            "target_calories":
                diet_plan.target_calories,

            "protein_g":
                diet_plan.target_protein_g,

            "carbohydrates_g":
                diet_plan.target_carbohydrates_g,

            "fat_g":
                diet_plan.target_fat_g,

            "fiber_g":
                diet_plan.target_fiber_g,
        },

        "weekly_plan":
            diet_plan.weekly_plan,
    }
    
# ============================================================
# GET DIET PLAN FOR SELECTED CALENDAR DATE
# ============================================================

@app.get(
    "/users/{user_id}/diet-plan/date/{selected_date}"
)
def get_diet_plan_by_date(
    user_id: int,
    selected_date: date,
    db: Session = Depends(get_db)
):
    # --------------------------------------------------------
    # FIND THE WEEKLY PLAN CONTAINING THIS DATE
    # --------------------------------------------------------

    diet_plan = (
        db.query(DietPlan)
        .filter(
            DietPlan.user_id == user_id,
            DietPlan.week_start_date <= selected_date,
            DietPlan.week_end_date >= selected_date,
        )
        .order_by(
            DietPlan.created_at.desc()
        )
        .first()
    )

    if not diet_plan:
        raise HTTPException(
            status_code=404,
            detail=(
                "No diet plan found for this date"
            )
        )

    weekly_plan = (
        diet_plan.weekly_plan
        if isinstance(
            diet_plan.weekly_plan,
            dict
        )
        else {}
    )

    days = weekly_plan.get(
        "days",
        []
    )

    # --------------------------------------------------------
    # FIND SELECTED DAY
    # --------------------------------------------------------

    selected_day = None

    for day_plan in days:
        if (
            day_plan.get("date")
            == selected_date.isoformat()
        ):
            selected_day = day_plan
            break

    if not selected_day:
        raise HTTPException(
            status_code=404,
            detail=(
                "Selected date is not available "
                "in the weekly plan"
            )
        )

    return {
        "diet_plan_id": diet_plan.id,

        "user_id": user_id,

        "date": selected_date.isoformat(),

        "week_start_date": (
            diet_plan.week_start_date.isoformat()
        ),

        "week_end_date": (
            diet_plan.week_end_date.isoformat()
        ),

        "nutrition_targets": {
            "target_calories":
                diet_plan.target_calories,

            "protein_g":
                diet_plan.target_protein_g,

            "carbohydrates_g":
                diet_plan.target_carbohydrates_g,

            "fat_g":
                diet_plan.target_fat_g,

            "fiber_g":
                diet_plan.target_fiber_g,
        },

        "day_plan": selected_day,
    }
# ============================================================
# GET LATEST SAVED DIET PLAN
# ============================================================

@app.get("/users/{user_id}/diet-plan")
def get_diet_plan(
    user_id: int,
    db: Session = Depends(get_db)
):
    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    diet_plan = (
        db.query(DietPlan)
        .filter(DietPlan.user_id == user_id)
        .order_by(DietPlan.created_at.desc())
        .first()
    )

    if not diet_plan:
        raise HTTPException(
            status_code=404,
            detail="No diet plan found for this user"
        )

    health_profile = (
        db.query(HealthProfile)
        .filter(HealthProfile.user_id == user_id)
        .first()
    )

    return {
        "diet_plan_id":
            diet_plan.id,

        "user_id":
            diet_plan.user_id,

        "goal": (
            health_profile.goal
            if health_profile
            else None
        ),

        "diet_preference": (
            health_profile.diet_preference
            if health_profile
            else None
        ),

        "women_health_condition": (
            health_profile.women_health_condition
            if health_profile
            else None
        ),

        "food_allergies":
            diet_plan.food_allergies,

        "foods_to_avoid":
            diet_plan.foods_to_avoid,

        "meals_per_day":
            diet_plan.meals_per_day,

        "nutrition_targets": {
            "bmr":
                diet_plan.bmr,

            "tdee":
                diet_plan.tdee,

            "target_calories":
                diet_plan.target_calories,

            "protein_g":
                diet_plan.target_protein_g,

            "carbohydrates_g":
                diet_plan.target_carbohydrates_g,

            "fat_g":
                diet_plan.target_fat_g,

            "fiber_g":
                diet_plan.target_fiber_g
        },

        "meals":
            diet_plan.meals,

        "daily_tip":
            diet_plan.daily_tip,

        "created_at":
            diet_plan.created_at
    }


# ============================================================
# DOWNLOAD LATEST SAVED DIET PLAN AS PDF
# ============================================================

@app.get("/users/{user_id}/diet-plan/pdf")
def download_diet_plan_pdf(
    user_id: int,
    db: Session = Depends(get_db)
):
    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    diet_plan = (
        db.query(DietPlan)
        .filter(DietPlan.user_id == user_id)
        .order_by(DietPlan.created_at.desc())
        .first()
    )

    if not diet_plan:
        raise HTTPException(
            status_code=404,
            detail="No diet plan found for this user"
        )

    health_profile = (
        db.query(HealthProfile)
        .filter(
            HealthProfile.user_id == user_id
        )
        .first()
    )

    pdf_buffer = BytesIO()

    document = SimpleDocTemplate(
        pdf_buffer,
        pagesize=A4,

        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,

        title="MealMind Personalized Diet Plan",
        author="MealMind"
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "MealMindTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=24,
        leading=29,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#047857"),
        spaceAfter=4 * mm,
    )

    subtitle_style = ParagraphStyle(
        "MealMindSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#64748B"),
        spaceAfter=8 * mm,
    )

    section_title_style = ParagraphStyle(
        "MealMindSection",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#065F46"),
        spaceBefore=5 * mm,
        spaceAfter=3 * mm,
    )

    meal_title_style = ParagraphStyle(
        "MealMindMealTitle",
        parent=styles["Heading3"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=15,
        textColor=colors.HexColor("#0F172A"),
        spaceAfter=2 * mm,
    )

    normal_style = ParagraphStyle(
        "MealMindNormal",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor("#334155"),
    )

    small_style = ParagraphStyle(
        "MealMindSmall",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#64748B"),
    )

    tip_style = ParagraphStyle(
        "MealMindTip",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=15,
        textColor=colors.HexColor("#065F46"),
    )

    story = []

    # --------------------------------------------------------
    # PDF HEADER
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "MealMind",
            title_style
        )
    )

    story.append(
        Paragraph(
            "Smart Nutrition, Made Personal.",
            subtitle_style
        )
    )

    story.append(
        Paragraph(
            "Personalized Diet Plan",
            section_title_style
        )
    )

    # --------------------------------------------------------
    # USER INFORMATION
    # --------------------------------------------------------

    goal = format_pdf_value(
        health_profile.goal
        if health_profile
        else None
    )

    diet_preference = format_pdf_value(
        health_profile.diet_preference
        if health_profile
        else None
    )

    activity_level = format_pdf_value(
        health_profile.activity_level
        if health_profile
        else None
    )

    user_data = [
        [
            "Name",
            safe_pdf_text(user.name),
            "Age",
            safe_pdf_text(user.age),
        ],

        [
            "Gender",
            format_pdf_value(user.gender),
            "Goal",
            goal,
        ],

        [
            "Height",
            f"{format_pdf_number(user.height_cm)} cm",
            "Weight",
            f"{format_pdf_number(user.weight_kg)} kg",
        ],

        [
            "Activity",
            activity_level,
            "Diet",
            diet_preference,
        ],
    ]

    user_table = Table(
        user_data,
        colWidths=[
            28 * mm,
            52 * mm,
            28 * mm,
            52 * mm,
        ],
    )

    user_table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (0, -1),
                colors.HexColor("#ECFDF5"),
            ),

            (
                "BACKGROUND",
                (2, 0),
                (2, -1),
                colors.HexColor("#ECFDF5"),
            ),

            (
                "TEXTCOLOR",
                (0, 0),
                (-1, -1),
                colors.HexColor("#334155"),
            ),

            (
                "FONTNAME",
                (0, 0),
                (-1, -1),
                "Helvetica",
            ),

            (
                "FONTNAME",
                (0, 0),
                (0, -1),
                "Helvetica-Bold",
            ),

            (
                "FONTNAME",
                (2, 0),
                (2, -1),
                "Helvetica-Bold",
            ),

            (
                "FONTSIZE",
                (0, 0),
                (-1, -1),
                9,
            ),

            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.4,
                colors.HexColor("#D1FAE5"),
            ),

            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE",
            ),

            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                7,
            ),

            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                7,
            ),

            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                7,
            ),

            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                7,
            ),
        ])
    )

    story.append(user_table)

    # --------------------------------------------------------
    # WOMEN'S HEALTH INFORMATION
    # --------------------------------------------------------

    women_health_condition = (
        health_profile.women_health_condition
        if health_profile
        else None
    )

    if (
        str(user.gender or "").lower().strip() == "female"
        and women_health_condition
        and str(women_health_condition).lower().strip() != "none"
    ):
        women_health_labels = {
            "pcos": "PCOS (Polycystic Ovary Syndrome)",
            "menstrual_wellness": "Menstrual Wellness",
            "pregnancy": "Pregnancy",
            "breastfeeding": "Breastfeeding",
        }

        normalized_women_health = (
            str(women_health_condition)
            .lower()
            .strip()
        )

        women_health_label = women_health_labels.get(
            normalized_women_health,
            format_pdf_value(women_health_condition),
        )

        story.append(
            Spacer(
                1,
                3 * mm
            )
        )

        story.append(
            Paragraph(
                "<b>Women's Health:</b> "
                + safe_pdf_text(women_health_label),
                normal_style
            )
        )

    story.append(
        Spacer(
            1,
            5 * mm
        )
    )

    # --------------------------------------------------------
    # DAILY NUTRITION TARGETS
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "Daily Nutrition Targets",
            section_title_style
        )
    )

    nutrition_data = [
        [
            "Calories",
            "Protein",
            "Carbohydrates",
            "Fat",
            "Fiber",
        ],

        [
            f"{format_pdf_number(diet_plan.target_calories)} kcal",
            f"{format_pdf_number(diet_plan.target_protein_g)} g",
            f"{format_pdf_number(diet_plan.target_carbohydrates_g)} g",
            f"{format_pdf_number(diet_plan.target_fat_g)} g",
            f"{format_pdf_number(diet_plan.target_fiber_g)} g",
        ],
    ]

    nutrition_table = Table(
        nutrition_data,
        colWidths=[
            32 * mm,
            32 * mm,
            36 * mm,
            30 * mm,
            30 * mm,
        ],
    )

    nutrition_table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor("#047857"),
            ),

            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.white,
            ),

            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold",
            ),

            (
                "BACKGROUND",
                (0, 1),
                (-1, 1),
                colors.HexColor("#F8FAFC"),
            ),

            (
                "TEXTCOLOR",
                (0, 1),
                (-1, 1),
                colors.HexColor("#0F172A"),
            ),

            (
                "FONTNAME",
                (0, 1),
                (-1, 1),
                "Helvetica-Bold",
            ),

            (
                "FONTSIZE",
                (0, 0),
                (-1, -1),
                8.5,
            ),

            (
                "ALIGN",
                (0, 0),
                (-1, -1),
                "CENTER",
            ),

            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE",
            ),

            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.4,
                colors.HexColor("#CBD5E1"),
            ),

            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                7,
            ),

            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                7,
            ),
        ])
    )

    story.append(nutrition_table)

    # --------------------------------------------------------
    # ALLERGIES + FOODS TO AVOID
    # --------------------------------------------------------

    allergies = (
        diet_plan.food_allergies
        if isinstance(
            diet_plan.food_allergies,
            list
        )
        else []
    )

    foods_to_avoid = (
        diet_plan.foods_to_avoid
        if isinstance(
            diet_plan.foods_to_avoid,
            list
        )
        else []
    )

    if allergies or foods_to_avoid:

        story.append(
            Paragraph(
                "Food Preferences & Restrictions",
                section_title_style
            )
        )

        if allergies:
            story.append(
                Paragraph(
                    "<b>Food allergies:</b> "
                    + safe_pdf_text(
                        ", ".join(
                            str(item)
                            for item in allergies
                        )
                    ),
                    normal_style
                )
            )

        if foods_to_avoid:
            story.append(
                Paragraph(
                    "<b>Foods to avoid:</b> "
                    + safe_pdf_text(
                        ", ".join(
                            str(item)
                            for item in foods_to_avoid
                        )
                    ),
                    normal_style
                )
            )
    # --------------------------------------------------------
    # DAILY MEAL PLAN
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "Daily Meal Plan",
            section_title_style
        )
    )

    meals = (
        diet_plan.meals
        if isinstance(
            diet_plan.meals,
            list
        )
        else []
    )

    for index, meal in enumerate(
        meals,
        start=1
    ):
        if not isinstance(meal, dict):
            continue

        meal_name = (
            meal.get("meal_name")
            or meal.get("name")
            or meal.get("meal")
            or f"Meal {index}"
        )

        estimated_calories = (
            meal.get("estimated_calories")
            or meal.get("calories")
            or 0
        )

        protein = (
            meal.get("protein_g")
            or 0
        )

        carbohydrates = (
            meal.get("carbohydrates_g")
            or 0
        )

        fat = (
            meal.get("fat_g")
            or 0
        )

        fiber = (
            meal.get("fiber_g")
            or 0
        )

        meal_elements = []

        meal_elements.append(
            Paragraph(
                f"{index}. "
                f"{safe_pdf_text(meal_name)}",
                meal_title_style
            )
        )

        meal_nutrition_data = [
            [
                "Calories",
                "Protein",
                "Carbs",
                "Fat",
                "Fiber",
            ],

            [
                f"{format_pdf_number(estimated_calories)} kcal",
                f"{format_pdf_number(protein)} g",
                f"{format_pdf_number(carbohydrates)} g",
                f"{format_pdf_number(fat)} g",
                f"{format_pdf_number(fiber)} g",
            ],
        ]

        meal_nutrition_table = Table(
            meal_nutrition_data,
            colWidths=[
                31 * mm,
                31 * mm,
                31 * mm,
                31 * mm,
                31 * mm,
            ],
        )

        meal_nutrition_table.setStyle(
            TableStyle([
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#F1F5F9"),
                ),

                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#475569"),
                ),

                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold",
                ),

                (
                    "FONTNAME",
                    (0, 1),
                    (-1, 1),
                    "Helvetica",
                ),

                (
                    "FONTSIZE",
                    (0, 0),
                    (-1, -1),
                    8,
                ),

                (
                    "ALIGN",
                    (0, 0),
                    (-1, -1),
                    "CENTER",
                ),

                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),

                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.3,
                    colors.HexColor("#E2E8F0"),
                ),

                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    5,
                ),

                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    5,
                ),
            ])
        )

        meal_elements.append(
            meal_nutrition_table
        )

        meal_elements.append(
            Spacer(
                1,
                2.5 * mm
            )
        )

        foods = (
            meal.get("foods")
            or meal.get("items")
            or meal.get("food_items")
            or []
        )

        if isinstance(foods, list):

            food_rows = [
                [
                    "Food",
                    "Portion",
                ]
            ]

            for food in foods:

                if isinstance(
                    food,
                    dict
                ):
                    food_name = (
                        food.get("food_name")
                        or food.get("name")
                        or "Food"
                    )

                    portion = (
                        food.get("portion")
                        or food.get("approximate_portion")
                        or "-"
                    )

                else:
                    food_name = str(food)
                    portion = "-"

                food_rows.append([
                    Paragraph(
                        safe_pdf_text(
                            food_name
                        ),
                        small_style
                    ),

                    Paragraph(
                        safe_pdf_text(
                            portion
                        ),
                        small_style
                    ),
                ])

            if len(food_rows) > 1:

                food_table = Table(
                    food_rows,
                    colWidths=[
                        100 * mm,
                        55 * mm,
                    ],
                )

                food_table.setStyle(
                    TableStyle([
                        (
                            "BACKGROUND",
                            (0, 0),
                            (-1, 0),
                            colors.HexColor("#ECFDF5"),
                        ),

                        (
                            "FONTNAME",
                            (0, 0),
                            (-1, 0),
                            "Helvetica-Bold",
                        ),

                        (
                            "TEXTCOLOR",
                            (0, 0),
                            (-1, 0),
                            colors.HexColor("#065F46"),
                        ),

                        (
                            "GRID",
                            (0, 0),
                            (-1, -1),
                            0.3,
                            colors.HexColor("#D1D5DB"),
                        ),

                        (
                            "VALIGN",
                            (0, 0),
                            (-1, -1),
                            "TOP",
                        ),

                        (
                            "LEFTPADDING",
                            (0, 0),
                            (-1, -1),
                            6,
                        ),

                        (
                            "RIGHTPADDING",
                            (0, 0),
                            (-1, -1),
                            6,
                        ),

                        (
                            "TOPPADDING",
                            (0, 0),
                            (-1, -1),
                            5,
                        ),

                        (
                            "BOTTOMPADDING",
                            (0, 0),
                            (-1, -1),
                            5,
                        ),
                    ])
                )

                meal_elements.append(
                    food_table
                )

        meal_elements.append(
            Spacer(
                1,
                5 * mm
            )
        )

        story.append(
            KeepTogether(
                meal_elements
            )
        )

    # --------------------------------------------------------
    # DAILY TIP
    # --------------------------------------------------------

    if diet_plan.daily_tip:

        story.append(
            Paragraph(
                "Daily Tip",
                section_title_style
            )
        )

        tip_table = Table(
            [[
                Paragraph(
                    safe_pdf_text(
                        diet_plan.daily_tip
                    ),
                    tip_style
                )
            ]],
            colWidths=[
                160 * mm
            ],
        )

        tip_table.setStyle(
            TableStyle([
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    colors.HexColor("#ECFDF5"),
                ),

                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.8,
                    colors.HexColor("#A7F3D0"),
                ),

                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    10,
                ),

                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    10,
                ),

                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    10,
                ),

                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    10,
                ),
            ])
        )

        story.append(
            tip_table
        )

    # --------------------------------------------------------
    # PLAN INFORMATION
    # --------------------------------------------------------

    story.append(
        Spacer(
            1,
            8 * mm
        )
    )

    if diet_plan.created_at:
        generated_date = (
            diet_plan.created_at.strftime(
                "%d %B %Y"
            )
        )

    else:
        generated_date = "Not available"

    story.append(
        Paragraph(
            f"Plan generated: "
            f"{safe_pdf_text(generated_date)}",
            small_style
        )
    )

    story.append(
        Spacer(
            1,
            2 * mm
        )
    )

    story.append(
        Paragraph(
            "MealMind - Smart Nutrition, Made Personal.",
            small_style
        )
    )

    story.append(
        Spacer(
            1,
            2 * mm
        )
    )

    story.append(
        Paragraph(
            "Nutrition values are estimates and this plan "
            "is intended for general wellness guidance.",
            small_style
        )
    )

    # --------------------------------------------------------
    # BUILD PDF
    # --------------------------------------------------------

    try:
        document.build(
            story,
            onFirstPage=add_pdf_page_number,
            onLaterPages=add_pdf_page_number,
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"PDF generation failed: {str(e)}"
        )

    pdf_buffer.seek(0)

    filename = (
        f"MealMind_Diet_Plan_"
        f"{user_id}.pdf"
    )

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
                f'attachment; filename="{filename}"'
        }
    )


# ============================================================
# PDF HELPER FUNCTIONS
# ============================================================

def safe_pdf_text(value):
    """
    Convert a value to safe text for ReportLab Paragraphs.
    """

    if value is None:
        return "-"

    text = str(value)

    text = text.replace(
        "&",
        "&amp;"
    )

    text = text.replace(
        "<",
        "&lt;"
    )

    text = text.replace(
        ">",
        "&gt;"
    )

    return text


def format_pdf_number(value):
    """
    Display numbers cleanly.
    """

    if value is None:
        return "-"

    try:
        number = float(value)

        if number.is_integer():
            return str(
                int(number)
            )

        return str(
            round(number, 1)
        )

    except (
        TypeError,
        ValueError
    ):
        return str(value)


def format_pdf_value(value):
    """
    Convert values such as:
    weight_loss -> Weight Loss
    non-vegetarian -> Non Vegetarian
    very_active -> Very Active
    """

    if value is None:
        return "-"

    return (
        str(value)
        .replace("_", " ")
        .replace("-", " ")
        .title()
    )


def add_pdf_page_number(
    canvas,
    document
):
    """
    Add page number at the bottom of every PDF page.
    """

    canvas.saveState()

    page_number = (
        canvas.getPageNumber()
    )

    page_width, _ = A4

    canvas.setFont(
        "Helvetica",
        8
    )

# ============================================================
# FORGOT PASSWORD - SEND OTP
# ============================================================

@app.post("/auth/forgot-password")
def forgot_password(
    request: ForgotPasswordRequest,
    db: Session = Depends(get_db)
):
    # Generic response for security.
    generic_response = {
        "message": (
            "If an account exists for this email, "
            "a verification code has been sent."
        )
    }

    # Normalize email.
    normalized_email = (
        request.email
        .lower()
        .strip()
    )

    # Find user in database.
    user = (
        db.query(User)
        .filter(
            User.email == normalized_email
        )
        .first()
    )

    # If user does not exist.
    if not user:
        print("DEBUG: User NOT found")
        return generic_response

    print("DEBUG: User found")

    # Mark previous unused OTPs as used.
    (
        db.query(PasswordResetOTP)
        .filter(
            PasswordResetOTP.user_id == user.id,
            PasswordResetOTP.used == False,
        )
        .update(
            {
                "used": True
            },
            synchronize_session=False
        )
    )

    # Generate new OTP.
    otp = generate_otp()

    # Create OTP database record.
    otp_record = PasswordResetOTP(
        user_id=user.id,
        otp_hash=hash_otp(otp),
        expires_at=(
            datetime.now(timezone.utc)
            + timedelta(minutes=10)
        ),
        used=False
    )

    try:
        # Save OTP record.
        db.add(otp_record)
        db.commit()
        db.refresh(otp_record)

        print(
            "DEBUG: Attempting to send OTP email"
        )

        # Send OTP through Gmail SMTP.
        send_password_reset_otp(
            receiver_email=user.email,
            otp=otp
        )

        print(
            "DEBUG: OTP email sent successfully"
        )

    except Exception as exc:
        db.rollback()

        print(
            "Password reset OTP error:",
            exc
        )

        return generic_response

    return generic_response
@app.post("/auth/verify-reset-otp")
def verify_reset_code(
    request: VerifyResetOTPRequest,
    db: Session = Depends(get_db)
):
    user = (
        db.query(User)
        .filter(
            User.email == request.email
        )
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired verification code."
        )

    record = (
        db.query(PasswordResetOTP)
        .filter(
            PasswordResetOTP.user_id == user.id,
            PasswordResetOTP.used == False,
        )
        .order_by(
            PasswordResetOTP.created_at.desc()
        )
        .first()
    )

    if not record:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired verification code."
        )

    now = datetime.now(timezone.utc)

    if record.expires_at < now:
        raise HTTPException(
            status_code=400,
            detail="Verification code has expired."
        )

    if not verify_otp(
        request.otp,
        record.otp_hash
    ):
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired verification code."
        )

    return {
        "message": "Verification code is valid."
    }
    
    @app.post("/auth/reset-password")
    def reset_password(
    request: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
        user = (
        db.query(User)
        .filter(
            User.email == request.email
        )
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired verification code."
        )

    record = (
        db.query(PasswordResetOTP)
        .filter(
            PasswordResetOTP.user_id == user.id,
            PasswordResetOTP.used == False,
        )
        .order_by(
            PasswordResetOTP.created_at.desc()
        )
        .first()
    )

    if not record:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired verification code."
        )

    now = datetime.now(timezone.utc)

    if record.expires_at < now:
        raise HTTPException(
            status_code=400,
            detail="Verification code has expired."
        )

    if not verify_otp(
        request.otp,
        record.otp_hash
    ):
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired verification code."
        )

    user.password_hash = hash_password(
        request.new_password
    )

    record.used = True

    db.commit()

    return {
        "message": (
            "Password reset successfully. "
            "You can now sign in."
        )
    }
    
    @app.post("/auth/change-password")
    def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db)
):
        if not verify_password(
        request.current_password,
        current_user.password_hash
    ):
            raise HTTPException(
            status_code=400,
            detail="Current password is incorrect."
        )

    if verify_password(
        request.new_password,
        current_user.password_hash
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                "New password must be different "
                "from the current password."
            )
        )

    current_user.password_hash = (
        hash_password(
            request.new_password
        )
    )

    db.commit()

    return {
        "message": "Password changed successfully."
    }
    
    from db_models.calendar_event import (
    CalendarEvent,
)

from models.calendar_event import (
    CalendarEventCreate,
    CalendarEventUpdate,
    CalendarEventResponse,
)

# ==========================================
# CUSTOM CALENDAR EVENTS
# ==========================================


@app.post(
    "/users/{user_id}/calendar-events",
    response_model=CalendarEventResponse,
)
def create_calendar_event(
    user_id: int,
    data: CalendarEventCreate,
    db: Session = Depends(get_db),
):
    event = CalendarEvent(
        user_id=user_id,
        event_date=data.event_date,
        start_time=data.start_time,
        title=data.title.strip(),
        notes=(
            data.notes.strip()
            if data.notes
            else None
        ),
    )

    db.add(event)

    db.commit()

    db.refresh(event)

    return event


@app.get(
    "/users/{user_id}/calendar-events",
    response_model=list[
        CalendarEventResponse
    ],
)
def get_calendar_events(
    user_id: int,
    date: date | None = None,
    db: Session = Depends(get_db),
):
    query = (
        db.query(CalendarEvent)
        .filter(
            CalendarEvent.user_id
            == user_id
        )
    )

    if date is not None:
        query = query.filter(
            CalendarEvent.event_date
            == date
        )

    events = (
        query
        .order_by(
            CalendarEvent.event_date.asc(),
            CalendarEvent.start_time.asc(),
        )
        .all()
    )

    return events


@app.patch(
    "/users/{user_id}/calendar-events/{event_id}",
    response_model=CalendarEventResponse,
)
def update_calendar_event(
    user_id: int,
    event_id: int,
    data: CalendarEventUpdate,
    db: Session = Depends(get_db),
):
    event = (
        db.query(CalendarEvent)
        .filter(
            CalendarEvent.id
            == event_id,
            CalendarEvent.user_id
            == user_id,
        )
        .first()
    )

    if not event:
        raise HTTPException(
            status_code=404,
            detail="Calendar event not found",
        )

    update_data = (
        data.model_dump(
            exclude_unset=True
        )
    )

    if "title" in update_data:
        update_data["title"] = (
            update_data["title"].strip()
        )

    if (
        "notes" in update_data
        and update_data["notes"]
    ):
        update_data["notes"] = (
            update_data["notes"].strip()
        )

    for field, value in (
        update_data.items()
    ):
        setattr(
            event,
            field,
            value,
        )

    db.commit()

    db.refresh(event)

    return event


@app.delete(
    "/users/{user_id}/calendar-events/{event_id}"
)
def delete_calendar_event(
    user_id: int,
    event_id: int,
    db: Session = Depends(get_db),
):
    event = (
        db.query(CalendarEvent)
        .filter(
            CalendarEvent.id
            == event_id,
            CalendarEvent.user_id
            == user_id,
        )
        .first()
    )

    if not event:
        raise HTTPException(
            status_code=404,
            detail="Calendar event not found",
        )

    db.delete(event)

    db.commit()

    return {
        "message":
            "Calendar event deleted"
    }
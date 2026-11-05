from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Date,
    DateTime,
    ForeignKey,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

from database import Base


class HealthReport(Base):
    __tablename__ = "health_reports"

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
        index=True
    )

    # Original uploaded filename
    original_filename = Column(
        String(255),
        nullable=False
    )

    # Local/cloud storage location of the report.
    # For V1 this can point to our local health_reports folder.
    file_path = Column(
        Text,
        nullable=True
    )

    # Examples:
    # image/jpeg
    # image/png
    # application/pdf
    file_type = Column(
        String(100),
        nullable=True
    )

    # Date mentioned on the health report.
    # This may be different from upload date.
    report_date = Column(
        Date,
        nullable=True
    )

    # Complete structured information extracted from
    # the report before/after user confirmation.
    #
    # Example:
    # {
    #     "blood_sugar_mg_dl": 300,
    #     "systolic_bp": null,
    #     "diastolic_bp": null,
    #     "thyroid_status": null,
    #     "additional_health_info": [...]
    # }
    extracted_data = Column(
        JSONB,
        nullable=True
    )

    # Human-readable extra health information that does
    # not have dedicated HealthProfile columns.
    additional_health_info = Column(
        Text,
        nullable=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
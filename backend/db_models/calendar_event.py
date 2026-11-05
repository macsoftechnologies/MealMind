from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Date,
    Time,
    DateTime,
    ForeignKey,
)

from sqlalchemy.sql import func

from database import Base


class CalendarEvent(Base):
    __tablename__ = "calendar_events"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_id = Column(
        Integer,
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    event_date = Column(
        Date,
        nullable=False,
        index=True,
    )

    start_time = Column(
        Time,
        nullable=False,
    )

    title = Column(
        String(200),
        nullable=False,
    )

    notes = Column(
        Text,
        nullable=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
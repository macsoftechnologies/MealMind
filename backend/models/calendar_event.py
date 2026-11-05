from datetime import (
    date,
    time,
    datetime,
)

from typing import Optional

from pydantic import (
    BaseModel,
    Field,
)


class CalendarEventCreate(
    BaseModel
):
    event_date: date

    start_time: time

    title: str = Field(
        ...,
        min_length=1,
        max_length=200,
    )

    notes: Optional[str] = None


class CalendarEventUpdate(
    BaseModel
):
    event_date: Optional[
        date
    ] = None

    start_time: Optional[
        time
    ] = None

    title: Optional[str] = Field(
        None,
        min_length=1,
        max_length=200,
    )

    notes: Optional[str] = None


class CalendarEventResponse(
    BaseModel
):
    id: int
    user_id: int

    event_date: date
    start_time: time

    title: str

    notes: Optional[str]

    created_at: datetime

    updated_at: datetime

    model_config = {
        "from_attributes": True
    }
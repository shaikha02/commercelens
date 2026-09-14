from datetime import datetime

from pydantic import BaseModel, field_validator


class Event(BaseModel):
    event_id: str
    invoice_id: str
    event_type: str
    status: str
    timestamp: datetime
    message: str
    error_message: str | None = None

    @field_validator("timestamp")
    @classmethod
    def timestamp_must_be_timezone_aware(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("timestamp must be timezone-aware")
        return value

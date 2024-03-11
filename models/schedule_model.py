from typing import Optional
from pydantic import validator
from datetime import datetime
from models.common_model import CommonModel, PyObjectId


class ScheduleCreate(CommonModel):
    drone: Optional[PyObjectId] = None
    mission: Optional[PyObjectId] = None
    start: datetime
    end: datetime
    status: str

    @validator('end')
    def validate_start_end(cls, end, values):
        start = values.get('start')
        if start and end.replace(tzinfo=None) <= start.replace(tzinfo=None):
            raise ValueError('End time must be after start time')
        return end
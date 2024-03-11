from typing import List, Optional
from pydantic import root_validator
from enum import Enum
from models.common_model import CommonModel, PyObjectId


class Status(str, Enum):
    available = "available"
    occupied = "occupied"


class DroneCreate(CommonModel):
    name: str
    status: Status  # Use the Status enum here
    current_mission_id: Optional[PyObjectId] = None
    possible_trajectories_ids: List[PyObjectId] = []
    possible_products_ids: List[PyObjectId] = []
    image: Optional[str] = None

    @root_validator(skip_on_failure=True)
    def check_mission_id(cls, values):
        status, current_mission_id = values.get('status'), values.get('current_mission_id')
        if status == Status.occupied and current_mission_id is None:
            raise ValueError('current_mission_id is required when status is "occupied"')
        elif status == Status.available and current_mission_id is not None:
            raise ValueError('current_mission_id must be None when status is "available"')
        return values

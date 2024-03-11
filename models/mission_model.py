from typing import Optional
from models.common_model import CommonModel, PyObjectId


class MissionCreate(CommonModel):
    name: str
    trajectory: Optional[PyObjectId] = None
    duration: int
    priority: int
    client: str
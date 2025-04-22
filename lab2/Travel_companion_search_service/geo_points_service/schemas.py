from pydantic import BaseModel, ConfigDict


class PointBase(BaseModel):
    id: int
    pointName: str
    px: float
    py: float

class PointResponse(PointBase):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 1,
                "pointName": "Kaluga",
                "px": 54.5293,
                "py": 36.2754
            }
        }
    )
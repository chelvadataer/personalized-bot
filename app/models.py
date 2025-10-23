from pydantic import BaseModel, Field


class Cab(BaseModel):
    cab_model_name: str = Field(..., min_length=1)
    cab_reg_name: str = Field(..., min_length=1)


class CabLocationUpdate(BaseModel):
    current_lat: float
    current_lan: float

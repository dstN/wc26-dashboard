from pydantic import BaseModel, ConfigDict, Field


class PhaseSchema(BaseModel):
    name: str = Field(alias="phase_name")
    pct: float
    group: str = Field(alias="phase_group")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

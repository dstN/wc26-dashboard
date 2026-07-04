from pydantic import BaseModel, ConfigDict, Field


class LineBreakSchema(BaseModel):
    line: str = Field(alias="line_type")
    attempted: int
    completed: int

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

from pydantic import BaseModel, ConfigDict, Field


class FinalThirdEntrySchema(BaseModel):
    zone: str
    count: int = Field(validation_alias="entry_count")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

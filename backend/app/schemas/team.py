from pydantic import BaseModel, ConfigDict


class TeamSchema(BaseModel):
    id: int
    name: str
    short_code: str
    slug: str
    color: str

    model_config = ConfigDict(from_attributes=True)

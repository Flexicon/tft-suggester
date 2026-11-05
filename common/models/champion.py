from pydantic import BaseModel, Field


class Champion(BaseModel):
    name: str
    image: str
    cost: int
    traits: list[str] = Field(default_factory=list)

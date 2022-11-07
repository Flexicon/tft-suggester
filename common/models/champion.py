from pydantic import BaseModel


class Champion(BaseModel):
    name: str
    image: str
    cost: int

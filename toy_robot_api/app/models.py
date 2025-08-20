from pydantic import BaseModel
from app.robot import Direction

class PlaceRequest(BaseModel):
    x: int
    y: int
    face: Direction

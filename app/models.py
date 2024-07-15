from pydantic import BaseModel
from typing import List


class HistoryItem(BaseModel):
    cycle: int
    icon: str


class DataModel(BaseModel):
    settings: List[float]
    history: List[HistoryItem]


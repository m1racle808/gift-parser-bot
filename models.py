from pydantic import BaseModel
from typing import Optional

class Gift(BaseModel):
    gift_id: str
    platform: str
    title: str
    price: float
    model: Optional[str] = None
    background: Optional[str] = None
    url: str

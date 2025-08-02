from pydantic import BaseModel
from typing import Optional

class GuestCreate(BaseModel):
    name: str
    is_attending: bool
    message: Optional[str] = None
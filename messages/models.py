from pydantic import BaseModel, EmailStr
from datetime import date
from typing import Optional
import base64

from enum import Enum



class message(BaseModel):
    # id:str
    receiver: str
    content : str
    timestamp: Optional[str]


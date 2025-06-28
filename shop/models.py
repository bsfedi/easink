from pydantic import BaseModel, EmailStr
from datetime import date
from typing import Optional
import base64

from enum import Enum



class shop(BaseModel):
    # id:str
    name: str
    city : str
    lat: float
    lng: float
    images: Optional[list]


from pydantic import BaseModel, EmailStr
from datetime import date
from typing import Optional
import base64

from enum import Enum



class Artiste(BaseModel):
    # id:str
    name: str
    studio: str
    ville: Optional[str]
    rate: Optional[str]
    images: Optional[list]
    next_availability: Optional[str] 

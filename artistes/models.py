from pydantic import BaseModel, EmailStr
from datetime import date
from typing import Optional
import base64

from enum import Enum



class Artiste(BaseModel):
    # id:str
    name: str
    shops: Optional[list]
    rate: Optional[str]
    tatouages: Optional[list]
    flashs: Optional[list]
    tags: Optional[list]
    next_availability: Optional[date] 

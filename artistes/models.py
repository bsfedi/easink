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
    description: Optional[str]
    informations: Optional[dict]
    avis: Optional[list]
    questions: Optional[list]
    tatouages: Optional[list]
    sub_tags :Optional[list]
    flashs: Optional[list]
    tags: Optional[list]
    next_availability: Optional[date] 

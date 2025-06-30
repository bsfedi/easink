from pydantic import BaseModel, EmailStr
from datetime import date
from typing import Optional
import base64

from enum import Enum



class flash_tatouages(BaseModel):
    # id:str

    shop: str
    image: Optional[str]
    artiste: Optional[str]
    tags : Optional[list]
    category: Optional[str] 
    description:Optional[str]
    type: Optional[str]
    prix : Optional[float]

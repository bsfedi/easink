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


class Reserver_flash(BaseModel):
    flash_id: str
    user_id: str
    taille: Optional[str] = None
    emplacement: Optional[str] = None
    date: Optional[date] 
    heure: Optional[str] = None
    shop_id: Optional[str] = None
    status: Optional[str] = "en attente"

class Project_flash(BaseModel):
    id: str
    image: Optional[str]
    type: Optional[str]
    description: Optional[str]
    prix: Optional[float]
    tags: Optional[list] = []
    artiste: Optional[str] = None
    shop: Optional[str] = None

class favorite_flash(BaseModel):
    favorite: bool = True
    flash_id: str


class favorite_tato(BaseModel):
    favorite: bool = True
    tato_id: str

    
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


class favorite_artiste(BaseModel):
    favorite: bool = True
    artiste_id: str

class Project(BaseModel):

    images: Optional[list]
    description: str
    taille: str
    emplacement: str
    budget: str
    status: str
    artiste_id: str

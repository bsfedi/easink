from pydantic import BaseModel, EmailStr
from datetime import date
from typing import Optional
import base64

from enum import Enum



class User(BaseModel):
    # id:str
    prenom: str
    email: EmailStr
    password: Optional[str]
    created_on: Optional[date]
    img_url: Optional[str] = None
    verified_email: Optional[bool] = False
    invitation_status: Optional[str] = "Pending"
    role: str


class Edit_user(BaseModel):
    first_name: str
    last_name: str
    password: str
    img_url: Optional[str] = None


class User_password(BaseModel):
    password: str


class new_password_user(BaseModel):
    old_password: str
    new_password: str


class User_email(BaseModel):
    email: EmailStr


class User_role(BaseModel):
    role: Optional[list] = []


class User_login(BaseModel):
    email: EmailStr
    password: str


class Domaine(BaseModel):
    # id:str
    name: str



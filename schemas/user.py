from pydantic import BaseModel, EmailStr, validator
from models.user import RoleEnum
from datetime import datetime
from typing import Optional

class UserCreate(BaseModel):
    email: EmailStr
    name:str
    mobile: int
    password: str
    @validator('mobile')
    def mobile_must_be_10_digits(cls, v):
        if len(str(v)) != 10:
            raise ValueError('Mobile number must be exactly 10 digits')
        return v

class UserOut(BaseModel):
    id: int
    email: EmailStr
    name:str
    mobile:int
    role: RoleEnum   

    model_config = {
        "from_attributes": True
    }

class Token(BaseModel):
    access_token: str
    refresh_token : str
    token_type: str



class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    mobile: Optional[int] = None


from datetime import datetime
from typing import Optional, List, Any

from pydantic import BaseModel, EmailStr, Field


#BASIS CLASSES
class UserBase(BaseModel):
    name: str = Field(..., max_length=255)
    email: EmailStr = Field(..., max_length=255)
    age: int = Field(..., ge=0, le=150)
    profile_picture: Optional[bytes] = None

class WeightingBase(BaseModel):
    user_id: int = Field(...)
    result: int = Field(..., max_digits=5, decimal_places=2) #May be need to change int to Decimal. We'll see.
    picture: Optional[bytes] = None
    creation_date: Optional[datetime] = datetime.utcnow()

class MealBase(BaseModel):
    user_id: int = Field(...)
    picture: Optional[bytes] = None
    creation_date: Optional[datetime] = None

class ProductBase(BaseModel):
    title: str = Field(..., max_length=255)
    proteins: int = Field(..., ge=0)
    fats: int = Field(..., ge=0)
    carbs: int = Field(..., ge=0)
    picture: Optional[bytes] = None

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


#QUERIES
class UserCreate(UserBase):
    name: str = Field(..., max_length=255)
    email: EmailStr = Field(..., max_length=255)
    password: str = Field(..., max_length=255)
    age: int = Field(..., ge=0, le=150)

class UserLogin(BaseModel):
    email: EmailStr = Field(..., max_length=255)
    password: str = Field(..., max_length=255)


#QUERIES RESPONSES
class UserResponse(BaseModel):
    id: int

Token.model_rebuild()

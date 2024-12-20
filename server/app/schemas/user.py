from pydantic import BaseModel, EmailStr
from typing import Optional
from app.models.user import CompanySize, WorkArea, Department

class UserCreate(BaseModel):
    id: Optional[str] = None
    name: str
    email: EmailStr
    phone: str
    company_name: Optional[str]
    company_size: Optional[CompanySize]
    work_area: WorkArea
    department: Department
    password: str
    accepted_privacy_policy: bool

class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone: str
    is_verified: bool

    class Config:
        orm_mode = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

from typing import Optional
from pydantic import BaseModel, EmailStr, Field, condecimal

# Users 
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    phone_number: str = Field(min_length=7, max_length=15)

class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone_number: str

    class Config:
        from_attributes = True

# Loan Requests
class LoanCreate(BaseModel):
    user_id: int
    amount: condecimal(gt=0, lt=1000000)

class LoanOut(BaseModel):
    id: int
    user_id: int
    amount: float
    status: str
    created_at: str
    updated_at: str
    class Config:
        from_attributes = True
    
class WebhookIn(BaseModel):
    load_id: int
    score: int
    status: str
    reason: Optional[str] = None





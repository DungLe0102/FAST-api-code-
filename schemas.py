from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

# Auth
class Token(BaseModel):
    access_token: str
    token_type: str

# Role
class RoleCreate(BaseModel):
    name: str

class RoleResponse(RoleCreate):
    id: str
    class Config:
        from_attributes = True

# User
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    is_active: Optional[bool] = True

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: str
    created_at: datetime
    roles: List[RoleResponse] = []
    class Config:
        from_attributes = True

# Category
class CategoryCreate(BaseModel):
    name: str
    parent_id: Optional[str] = None

class CategoryResponse(CategoryCreate):
    id: str
    class Config:
        from_attributes = True

# Product
class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: Decimal
    stock: int
    category_id: str

class ProductResponse(ProductCreate):
    id: str
    is_active: bool
    created_at: datetime
    class Config:
        from_attributes = True

# Order
class OrderItemCreate(BaseModel):
    product_id: str
    quantity: int

class OrderItemResponse(OrderItemCreate):
    id: str
    price: Decimal
    class Config:
        from_attributes = True

class OrderCreate(BaseModel):
    items: List[OrderItemCreate]

class OrderResponse(BaseModel):
    id: str
    user_id: str
    status: str
    total_price: Decimal
    created_at: datetime
    items: List[OrderItemResponse]
    class Config:
        from_attributes = True

# Review
class ReviewCreate(BaseModel):
    product_id: str
    rating: int
    comment: Optional[str] = None

class ReviewResponse(ReviewCreate):
    id: str
    user_id: str
    created_at: datetime
    class Config:
        from_attributes = True

# Audit Log
class AuditLogResponse(BaseModel):
    id: str
    user_id: str
    action: str
    table_name: str
    created_at: datetime
    class Config:
        from_attributes = True
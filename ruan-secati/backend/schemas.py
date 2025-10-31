from pydantic import BaseModel, Field
from typing import Optional


class UserCreate(BaseModel):
    username: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class UserResponse(BaseModel):
    id: int
    username: str
    created_at: str


class HistoryRecord(BaseModel):
    user_id: int
    product1: str
    product2: str
    comparison_result: dict


class CompareRequest(BaseModel):
    product1: str = Field(..., min_length=1)
    product2: str = Field(..., min_length=1)

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date
import uuid

# ==================================
# USER SCHEMAS
# ==================================
class User(BaseModel):
    id: int = Field(..., example=101)
    name: str = Field(..., example="Steven Jerry")
    role: str = Field(..., example="mahasiswa")

    class Config:
        from_attributes = True


# ==================================
# BOOK SCHEMAS
# ==================================
class BookBase(BaseModel):
    title: str = Field(..., example="Pemrograman Python")
    author: str = Field(..., example="Guido van Rossum")
    stock: int = Field(..., ge=0, example=5)

class BookCreate(BookBase):
    pass

class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    stock: Optional[int] = Field(None, ge=0)

class Book(BookBase):
    id: uuid.UUID
    class Config:
        from_attributes = True


# ==================================
# LOAN / TRANSACTION SCHEMAS
# ==================================
class LoanRecord(BaseModel):
    id: uuid.UUID
    user_id: int
    book_id: uuid.UUID
    borrow_date: date
    due_date: date
    return_date: Optional[date] = None
    extended: bool = False
    initial_borrow_date: date
    fine: int = 0

class ActiveLoanResponse(BaseModel):
    loan_id: uuid.UUID
    book_id: uuid.UUID
    book_title: str
    borrow_date: date
    due_date: date
    extended: bool

class ReturnConfirmation(BaseModel):
    message: str
    loan_id: uuid.UUID
    fine_charged: int = 0

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date
import uuid

# =============== USER ===============
class User(BaseModel):
    id: int = Field(..., example=101)
    name: str = Field(..., example="Steven Jerry")
    role: str = Field(..., example="mahasiswa")
    class Config: from_attributes = True

# =============== BOOKS ===============
class Book(BaseModel):
    id: uuid.UUID
    title: str
    author: str
    stock: int = 0
    class Config: from_attributes = True

class BookCreate(BaseModel):
    title: str
    author: str
    stock: int = 0

class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    stock: Optional[int] = None

# =============== LOANS ===============
class LoanRecord(BaseModel):
    id: uuid.UUID
    user_id: int
    book_id: uuid.UUID
    borrow_date: date
    due_date: date
    initial_borrow_date: date
    return_date: Optional[date] = None
    extended: bool = False
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

# =============== HISTORY + SIMULASI ===============
class HistoryItem(BaseModel):
    loan_id: uuid.UUID
    user: str
    book: str
    borrow_date: date
    due_date: date
    return_date: Optional[date] = None
    status: str
    late_days: int
    fine: int

class FineSimulationResponse(BaseModel):
    loan_id: uuid.UUID
    book: str
    due_date: date
    planned_return: date
    late_days: int
    calculated_fine: int
    note: str

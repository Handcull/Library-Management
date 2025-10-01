from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date
import uuid

# ==================================
#         USER SCHEMAS
# ==================================
class User(BaseModel):
    """
    Model dasar untuk pengguna. Dalam sistem nyata, ini akan jauh lebih kompleks.
    """
    id: int = Field(..., example=101)
    role: str = Field(..., example="mahasiswa")  # 'admin' atau 'mahasiswa'

# ==================================
#         BOOK SCHEMAS
# ==================================
class BookBase(BaseModel):
    """
    Schema dasar untuk data buku.
    """
    title: str = Field(..., min_length=1, example="Pemrograman Python untuk Pemula")
    author: str = Field(..., min_length=1, example="Guido van Rossum")
    stock: int = Field(..., ge=0, example=10) # ge=0 berarti stok tidak boleh negatif

class BookCreate(BookBase):
    """
    Schema yang digunakan saat admin menambahkan buku baru.
    """
    pass

class BookUpdate(BaseModel):
    """
    Schema yang digunakan saat admin memperbarui data buku. Semua field bersifat opsional.
    """
    title: Optional[str] = Field(None, min_length=1)
    author: Optional[str] = Field(None, min_length=1)
    stock: Optional[int] = Field(None, ge=0)

class Book(BookBase):
    """
    Schema lengkap buku, termasuk ID, yang dikirim sebagai respons dari API.
    """
    id: uuid.UUID

    class Config:
        from_attributes = True


# ==================================
#      TRANSACTION SCHEMAS
# ==================================
class LoanRecord(BaseModel):
    """
    Schema untuk mencatat riwayat peminjaman buku.
    """
    id: uuid.UUID
    user_id: int
    book_id: uuid.UUID
    borrow_date: date
    due_date: date
    return_date: Optional[date] = None
    extended: bool = False
    initial_borrow_date: date # Untuk melacak tanggal awal pinjam demi aturan 30 hari
    fine: int = 0  # Dalam Rupiah

class ActiveLoanResponse(BaseModel):
    """
    Schema respons untuk menampilkan buku yang sedang dipinjam oleh pengguna.
    """
    loan_id: uuid.UUID
    book_id: uuid.UUID
    book_title: str
    borrow_date: date
    due_date: date
    extended: bool

class ReturnConfirmation(BaseModel):
    """
    Schema respons setelah buku dikembalikan.
    """
    message: str
    loan_id: uuid.UUID
    fine_charged: int = 0 # Denda yang dikenakan

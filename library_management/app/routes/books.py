from fastapi import APIRouter, HTTPException, status, Depends
import uuid
from typing import List
from ..schemas import Book, BookCreate, BookUpdate
from ..data_store import books_db
from ..dependencies import get_current_user, require_admin_role

router = APIRouter()

# ============ PUBLIC ============
@router.get("/", response_model=List[Book])
def get_all_books():
    """Dapatkan semua buku"""
    return list(books_db.values())

@router.get("/{book_id}", response_model=Book)
def get_book(book_id: uuid.UUID):
    """Dapatkan buku berdasarkan ID"""
    book = books_db.get(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Buku tidak ditemukan")
    return book


# ============ ADMIN ============
@router.post("/", response_model=Book, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin_role)])
def add_book(book: BookCreate):
    """Tambah buku baru oleh admin"""
    new_id = uuid.uuid4()
    new_book = Book(id=new_id, **book.model_dump())
    books_db[new_id] = new_book
    return new_book

@router.put("/{book_id}", response_model=Book, dependencies=[Depends(require_admin_role)])
def update_book(book_id: uuid.UUID, book: BookUpdate):
    """Update buku oleh admin"""
    existing = books_db.get(book_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Buku tidak ditemukan")

    updated = existing.model_copy(update=book.model_dump(exclude_unset=True))
    books_db[book_id] = updated
    return updated

@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_admin_role)])
def delete_book(book_id: uuid.UUID):
    """Hapus buku oleh admin"""
    if book_id not in books_db:
        raise HTTPException(status_code=404, detail="Buku tidak ditemukan")
    del books_db[book_id]

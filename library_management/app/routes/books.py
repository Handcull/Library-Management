# library_management/app/routes/books.py
from fastapi import APIRouter, HTTPException, status, Depends
import uuid
from typing import List
from ..schemas import Book, BookCreate, BookUpdate
from ..data_store import books_db
from ..dependencies import require_admin_role
from ..utils import success_response

router = APIRouter()

# ======== PUBLIC ========
@router.get("/")
def get_all_books():
    return success_response("Data buku berhasil diambil", list(books_db.values()))

@router.get("/{book_id}")
def get_book(book_id: uuid.UUID):
    book = books_db.get(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Buku dengan ID tersebut tidak ditemukan dalam sistem.")
    return success_response("Detail buku berhasil diambil", book)

# ======== ADMIN ========
@router.post("/", status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin_role)])
def create_book(book: BookCreate):
    new_id = uuid.uuid4()
    b = Book(id=new_id, **book.model_dump())
    books_db[new_id] = b
    return success_response("Buku baru berhasil ditambahkan", b)

@router.put("/{book_id}", dependencies=[Depends(require_admin_role)])
def update_book(book_id: uuid.UUID, book: BookUpdate):
    existing = books_db.get(book_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Buku dengan ID tersebut tidak ditemukan dalam sistem.")
    updated = existing.model_copy(update=book.model_dump(exclude_unset=True))
    books_db[book_id] = updated
    return success_response("Data buku berhasil diperbarui", updated)

@router.delete("/{book_id}", status_code=status.HTTP_200_OK, dependencies=[Depends(require_admin_role)])
def delete_book(book_id: uuid.UUID):
    if book_id not in books_db:
        raise HTTPException(status_code=404, detail="Buku dengan ID tersebut tidak ditemukan dalam sistem.")
    del books_db[book_id]
    return success_response("Buku berhasil dihapus", {"book_id": str(book_id)})

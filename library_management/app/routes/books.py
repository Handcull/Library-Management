from fastapi import APIRouter, HTTPException, status, Depends, Response
from typing import List
import uuid
from ..schemas import Book, BookCreate, BookUpdate, User
from ..data_store import books_db
from ..dependencies import require_admin_role, get_current_user

router = APIRouter(
    prefix="/books",
    tags=["Books Management (Admin)"],
    # Semua endpoint di file ini memerlukan peran admin
    dependencies=[Depends(require_admin_role)]
)

# Router terpisah untuk endpoint publik (GET)
public_router = APIRouter(
    prefix="/books",
    tags=["Books (Public)"]
)

@public_router.get("/", response_model=List[Book])
def get_all_books(available_only: bool = False):
    """
    Mendapatkan daftar semua buku. Bisa diakses oleh semua user.
    Jika query parameter `available_only` adalah true, hanya buku dengan stok > 0 yang ditampilkan.
    """
    book_list = list(books_db.values())
    if available_only:
        return [book for book in book_list if book.stock > 0]
    return book_list

@public_router.get("/{book_id}", response_model=Book)
def get_book_by_id(book_id: uuid.UUID):
    """
    Mendapatkan detail satu buku berdasarkan ID. Bisa diakses oleh semua user.
    """
    book = books_db.get(book_id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Buku tidak ditemukan.")
    return book


@router.post("/", response_model=Book, status_code=status.HTTP_201_CREATED)
def add_new_book(book_data: BookCreate):
    """
    Menambahkan buku baru ke dalam sistem. (Hanya Admin)
    """
    new_id = uuid.uuid4()
    # Pastikan tidak ada duplikat ID, meskipun kemungkinannya sangat kecil
    while new_id in books_db:
        new_id = uuid.uuid4()
    
    new_book = Book(id=new_id, **book_data.model_dump())
    books_db[new_id] = new_book
    return new_book

@router.put("/{book_id}", response_model=Book)
def update_book_details(book_id: uuid.UUID, book_update: BookUpdate):
    """
    Memperbarui informasi buku berdasarkan ID. (Hanya Admin)
    Hanya field yang diisi yang akan diperbarui.
    """
    book = books_db.get(book_id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Buku tidak ditemukan.")

    update_data = book_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(book, key, value)
    
    books_db[book_id] = book
    return book

@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: uuid.UUID):
    """
    Menghapus buku dari sistem berdasarkan ID. (Hanya Admin)
    """
    if book_id not in books_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Buku tidak ditemukan.")
    
    del books_db[book_id]
    return Response(status_code=status.HTTP_204_NO_CONTENT)

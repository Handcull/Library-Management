from fastapi import APIRouter, HTTPException, status, Depends
from datetime import date, timedelta
import uuid
from ..schemas import LoanRecord, ReturnConfirmation
from ..data_store import books_db, loans_db
from ..dependencies import get_current_user

router = APIRouter()

# ==========================================================
#                 PINJAM BUKU (BORROW)
# ==========================================================
@router.post("/borrow/{book_id}", response_model=LoanRecord, status_code=status.HTTP_201_CREATED)
def borrow_book(book_id: uuid.UUID, current_user=Depends(get_current_user)):
    """
    Endpoint untuk meminjam buku oleh pengguna dengan role 'mahasiswa'.
    - Jika stok buku habis → 400
    - Jika bukan mahasiswa → 403
    - Jika berhasil → 201 dan mengembalikan data LoanRecord
    """
    if current_user.role != "mahasiswa":
        raise HTTPException(status_code=403, detail="Hanya mahasiswa yang dapat meminjam buku")

    book = books_db.get(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Buku tidak ditemukan")
    if book.stock <= 0:
        raise HTTPException(status_code=400, detail="Stok habis")

    # Kurangi stok buku
    book.stock -= 1
    books_db[book_id] = book

    # Buat catatan peminjaman
    loan_id = uuid.uuid4()
    today = date.today()
    record = LoanRecord(
        id=loan_id,
        user_id=current_user.id,
        book_id=book_id,
        borrow_date=today,
        due_date=today + timedelta(days=7),
        initial_borrow_date=today
    )
    loans_db[loan_id] = record
    return record


# ==========================================================
#                 KEMBALIKAN BUKU (RETURN)
# ==========================================================
@router.post("/return/{loan_id}", response_model=ReturnConfirmation)
def return_book(loan_id: uuid.UUID, current_user=Depends(get_current_user)):
    """
    Endpoint untuk mengembalikan buku.
    - Jika pinjaman tidak ditemukan → 404
    - Jika buku sudah dikembalikan → 400
    - Jika terlambat → denda 2000 per hari
    - Jika berhasil → 200 OK + pesan konfirmasi
    """
    loan = loans_db.get(loan_id)
    if not loan:
        raise HTTPException(status_code=404, detail="Peminjaman tidak ditemukan")
    if loan.return_date:
        raise HTTPException(status_code=400, detail="Buku sudah dikembalikan")

    today = date.today()
    fine = 0
    if today > loan.due_date:
        fine = (today - loan.due_date).days * 2000  # denda 2000/hari

    loan.return_date = today
    loans_db[loan_id] = loan

    # Kembalikan stok buku
    book = books_db.get(loan.book_id)
    if book:
        book.stock += 1
        books_db[loan.book_id] = book

    return ReturnConfirmation(
        message="Buku berhasil dikembalikan",
        loan_id=loan_id,
        fine_charged=fine
    )


# ==========================================================
#                 PERPANJANG PEMINJAMAN (EXTEND)
# ==========================================================
@router.post("/extend/{loan_id}", response_model=LoanRecord)
def extend_loan(loan_id: uuid.UUID, current_user=Depends(get_current_user)):
    """
    Endpoint untuk memperpanjang masa peminjaman buku.
    - Hanya boleh diperpanjang 1 kali.
    - Jika pinjaman tidak ditemukan → 404
    - Jika sudah diperpanjang sebelumnya → 400
    """
    loan = loans_db.get(loan_id)
    if not loan:
        raise HTTPException(status_code=404, detail="Peminjaman tidak ditemukan")
    if loan.extended:
        raise HTTPException(status_code=400, detail="Sudah diperpanjang sekali")

    # Perpanjang jatuh tempo 7 hari
    loan.due_date += timedelta(days=7)
    loan.extended = True
    loans_db[loan_id] = loan
    return loan

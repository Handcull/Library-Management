from fastapi import APIRouter, HTTPException, status, Depends
from datetime import date, timedelta
import uuid
from typing import List

from ..schemas import User, LoanRecord, ReturnConfirmation, ActiveLoanResponse
from ..data_store import books_db, loans_db
from ..dependencies import get_current_user, require_admin_role

# === KONFIGURASI ATURAN PEMINJAMAN ===
LOAN_DURATION_DAYS = 14
MAX_LOAN_DAYS_TOTAL = 30
FINE_PER_DAY = 1000  # dalam Rupiah

router = APIRouter(
    tags=["Loan Transactions"]
)

@router.post("/borrow/{book_id}", response_model=LoanRecord, status_code=status.HTTP_201_CREATED)
def borrow_book(book_id: uuid.UUID, current_user: User = Depends(get_current_user)):
    """
    Endpoint untuk mahasiswa meminjam buku.
    """
    if current_user.role == 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin tidak dapat meminjam buku.")

    book = books_db.get(book_id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Buku tidak ditemukan.")
    
    if book.stock <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Stok buku habis.")

    # Cek apakah user sudah meminjam buku yang sama dan belum dikembalikan
    existing_loan = next((loan for loan in loans_db if loan.user_id == current_user.id and loan.book_id == book_id and loan.return_date is None), None)
    if existing_loan:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Anda sudah meminjam buku ini.")

    # Proses peminjaman
    book.stock -= 1
    today = date.today()
    
    new_loan = LoanRecord(
        id=uuid.uuid4(),
        user_id=current_user.id,
        book_id=book_id,
        borrow_date=today,
        due_date=today + timedelta(days=LOAN_DURATION_DAYS),
        initial_borrow_date=today, # Set tanggal pinjam awal
    )
    loans_db.append(new_loan)
    return new_loan

@router.post("/return/{loan_id}", response_model=ReturnConfirmation)
def return_book(loan_id: uuid.UUID, current_user: User = Depends(get_current_user)):
    """
    Endpoint untuk mahasiswa mengembalikan buku.
    """
    loan = next((l for l in loans_db if l.id == loan_id), None)
    
    if not loan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Data peminjaman tidak ditemukan.")

    if loan.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Anda tidak berhak mengembalikan pinjaman ini.")

    if loan.return_date is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Buku ini sudah dikembalikan.")

    # Proses pengembalian
    today = date.today()
    fine_charged = 0
    if today > loan.due_date:
        days_late = (today - loan.due_date).days
        fine_charged = days_late * FINE_PER_DAY
    
    loan.return_date = today
    loan.fine = fine_charged
    
    book = books_db.get(loan.book_id)
    if book:
        book.stock += 1
        
    return ReturnConfirmation(
        message="Buku berhasil dikembalikan.",
        loan_id=loan.id,
        fine_charged=fine_charged
    )

@router.post("/extend/{loan_id}", response_model=LoanRecord)
def extend_loan_period(loan_id: uuid.UUID, current_user: User = Depends(get_current_user)):
    """
    Endpoint untuk mahasiswa memperpanjang masa pinjam.
    """
    loan = next((l for l in loans_db if l.id == loan_id and l.user_id == current_user.id), None)

    if not loan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Data peminjaman tidak ditemukan.")
    
    if loan.return_date is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tidak dapat memperpanjang pinjaman yang sudah selesai.")

    if loan.extended:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Masa pinjam hanya bisa diperpanjang satu kali.")

    # Cek aturan 30 hari
    new_due_date = loan.due_date + timedelta(days=LOAN_DURATION_DAYS)
    total_loan_duration = (new_due_date - loan.initial_borrow_date).days
    if total_loan_duration > MAX_LOAN_DAYS_TOTAL:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Perpanjangan ditolak. Total durasi pinjam tidak boleh melebihi {MAX_LOAN_DAYS_TOTAL} hari.")

    loan.due_date = new_due_date
    loan.extended = True
    return loan

@router.get("/loans/my-loans", response_model=List[ActiveLoanResponse])
def get_my_active_loans(current_user: User = Depends(get_current_user)):
    """
    Melihat daftar buku yang sedang dipinjam oleh user saat ini.
    """
    active_loans = [
        loan for loan in loans_db 
        if loan.user_id == current_user.id and loan.return_date is None
    ]
    
    response = []
    for loan in active_loans:
        book = books_db.get(loan.book_id)
        response.append(ActiveLoanResponse(
            loan_id=loan.id,
            book_id=loan.book_id,
            book_title=book.title if book else "Buku Tidak Ditemukan",
            borrow_date=loan.borrow_date,
            due_date=loan.due_date,
            extended=loan.extended
        ))
    return response

@router.get("/loans/active-all", response_model=List[LoanRecord], dependencies=[Depends(require_admin_role)])
def get_all_active_loans():
    """
    Melihat semua buku yang sedang dipinjam di seluruh perpustakaan. (Hanya Admin)
    """
    return [loan for loan in loans_db if loan.return_date is None]

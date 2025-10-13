# library_management/app/routes/transactions.py
from fastapi import APIRouter, HTTPException, status, Depends, Query
from datetime import date, timedelta
import uuid

from ..schemas import LoanRecord
from ..data_store import (
    books_db, loans_db, users_db,
    FINE_PER_DAY, LOAN_LIMIT_DAYS
)
from ..dependencies import get_current_user
from ..utils import success_response, format_rupiah

router = APIRouter()

# ===================== UTIL =====================
def _row_with_status(loan: LoanRecord) -> dict:
    """Bangun satu baris informasi peminjaman yang informatif & profesional."""
    user = users_db.get(loan.user_id)
    book = books_db.get(loan.book_id)

    user_label = f"{(user.name if user else 'Pengguna')} (ID: {loan.user_id})"
    book_label = f"{(book.title if book else 'Buku')}{' by ' + book.author if book and book.author else ''}"

    today = date.today()
    # tanggal referensi untuk hitung keterlambatan
    effective_return = loan.return_date
    base_date = effective_return or today

    # hitung telat & denda berjalan (bila belum dikembalikan)
    late_days = max(0, (base_date - loan.due_date).days)
    running_fine = loan.fine if loan.return_date else late_days * FINE_PER_DAY

    # status text + status_code (BERJALAN/SELESAI/TERLAMBAT)
    if loan.return_date:
        status_text = "Dikembalikan"
        status_code = "SELESAI"
    else:
        if late_days > 0:
            status_text = "Dipinjam (terlambat)"
            status_code = "TERLAMBAT"
        else:
            status_text = "Dipinjam"
            status_code = "BERJALAN"

    # tambahkan info “(diperpanjang)” bila sudah extend
    if not loan.return_date and loan.extended and "Dipinjam" in status_text:
        status_text = "Dipinjam (diperpanjang)" if status_code == "BERJALAN" else status_text

    # total hari pinjam yang sedang berlaku (due_date terhadap tanggal awal)
    total_days_now = (loan.due_date - loan.initial_borrow_date).days

    # boleh_perpanjang? (belum pernah extend & jika tambah 7 hari tidak melebihi limit 30 hari)
    next_total_days = (loan.due_date + timedelta(days=7) - loan.initial_borrow_date).days
    boleh_perpanjang = (not loan.extended) and (next_total_days <= LOAN_LIMIT_DAYS) and (loan.return_date is None)

    # boleh_kembalikan? (belum dikembalikan)
    boleh_kembalikan = loan.return_date is None

    return {
        "loan_id": str(loan.id),
        "user": user_label,
        "book": book_label,
        "tanggal_pinjam": str(loan.borrow_date),
        "tanggal_jatuh_tempo": str(loan.due_date),
        "status": status_text,
        "status_code": status_code,                     # BERJALAN / SELESAI / TERLAMBAT
        "sudah_diperpanjang": bool(loan.extended),
        "total_hari_pinjam": total_days_now,            # dari tanggal awal s.d due_date saat ini
        "boleh_perpanjang": boleh_perpanjang,
        "boleh_kembalikan": boleh_kembalikan,
        "keterlambatan": f"{late_days} hari",
        "denda": format_rupiah(running_fine)
    }

# ===================== PINJAM =====================
@router.post("/borrow/{book_id}", status_code=status.HTTP_201_CREATED)
def borrow_book(book_id: uuid.UUID, current_user=Depends(get_current_user)):
    if current_user.role != "mahasiswa":
        raise HTTPException(status_code=403, detail="Akses ditolak. Hanya mahasiswa yang dapat melakukan peminjaman.")

    book = books_db.get(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Buku dengan ID tersebut tidak ditemukan dalam sistem.")
    if book.stock <= 0:
        raise HTTPException(status_code=400, detail="Peminjaman gagal karena stok buku saat ini kosong.")

    # stok --
    book.stock -= 1
    books_db[book_id] = book

    today = date.today()
    record = LoanRecord(
        id=uuid.uuid4(),
        user_id=current_user.id,
        book_id=book_id,
        borrow_date=today,
        due_date=today + timedelta(days=7),
        initial_borrow_date=today
    )
    loans_db[record.id] = record

    return success_response(
        "Peminjaman buku berhasil dibuat",
        {
            "loan_id": str(record.id),
            "user_id": record.user_id,
            "book_id": str(record.book_id),
            "tanggal_pinjam": str(record.borrow_date),
            "tanggal_jatuh_tempo": str(record.due_date),
            "status": "Dipinjam"
        }
    )

# ===================== KEMBALIKAN =====================
@router.post("/return/{loan_id}")
def return_book(loan_id: uuid.UUID, current_user=Depends(get_current_user)):
    loan = loans_db.get(loan_id)
    if not loan:
        raise HTTPException(status_code=404, detail="Data peminjaman tidak ditemukan dalam sistem.")
    if loan.return_date:
        raise HTTPException(status_code=400, detail="Pengembalian tidak dapat diproses karena buku sudah dikembalikan sebelumnya.")

    today = date.today()
    fine = 0
    if today > loan.due_date:
        fine = (today - loan.due_date).days * FINE_PER_DAY

    loan.return_date = today
    loan.fine = fine
    loans_db[loan_id] = loan

    # stok ++
    book = books_db.get(loan.book_id)
    if book:
        book.stock += 1
        books_db[loan.book_id] = book

    return success_response(
        "Pengembalian buku berhasil diproses",
        {
            "loan_id": str(loan_id),
            "tanggal_dikembalikan": str(today),
            "denda": format_rupiah(fine)
        }
    )

# ===================== PERPANJANG =====================
@router.post("/extend/{loan_id}")
def extend_loan(loan_id: uuid.UUID, current_user=Depends(get_current_user)):
    loan = loans_db.get(loan_id)
    if not loan:
        raise HTTPException(status_code=404, detail="Data peminjaman tidak ditemukan dalam sistem.")
    if loan.extended:
        raise HTTPException(status_code=400, detail="Peminjaman ini sudah pernah diperpanjang dan tidak dapat diperpanjang lagi.")

    total_days_if_extended = (loan.due_date + timedelta(days=7) - loan.initial_borrow_date).days
    if total_days_if_extended > LOAN_LIMIT_DAYS:
        raise HTTPException(status_code=400, detail="Perpanjangan ditolak karena total durasi pinjam akan melebihi 30 hari.")

    loan.due_date += timedelta(days=7)
    loan.extended = True
    loans_db[loan_id] = loan

    return success_response(
        "Perpanjangan peminjaman berhasil diproses",
        {
            "loan_id": str(loan.id),
            "tanggal_jatuh_tempo_baru": str(loan.due_date),
            "status": "Dipinjam (diperpanjang)",
        }
    )

# ===================== LOANS: ACTIVE =====================
@router.get("/loans/active")
def list_active_loans(current_user=Depends(get_current_user)):
    """
    Admin: melihat semua pinjaman yang masih aktif
    Mahasiswa: melihat pinjaman aktif miliknya
    """
    rows = []
    for loan in loans_db.values():
        if loan.return_date is not None:
            continue
        if current_user.role != "admin" and loan.user_id != current_user.id:
            continue
        rows.append(_row_with_status(loan))
    return success_response("Data pinjaman aktif berhasil diambil", rows)

# ===================== LOANS: HISTORY (ADMIN) =====================
@router.get("/loans/history")
def list_history_admin(current_user=Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Akses ditolak. Hanya admin yang dapat melihat seluruh riwayat peminjaman.")
    rows = [_row_with_status(loan) for loan in loans_db.values()]
    rows.sort(key=lambda r: (r["tanggal_pinjam"], r["tanggal_jatuh_tempo"]), reverse=True)
    return success_response("Riwayat peminjaman (semua pengguna) berhasil diambil", rows)

# ===================== LOANS: HISTORY (ME) =====================
@router.get("/loans/history/me")
def list_history_me(current_user=Depends(get_current_user)):
    rows = []
    for loan in loans_db.values():
        if loan.user_id == current_user.id:
            rows.append(_row_with_status(loan))
    rows.sort(key=lambda r: (r["tanggal_pinjam"], r["tanggal_jatuh_tempo"]), reverse=True)
    return success_response("Riwayat peminjaman Anda berhasil diambil", rows)

# ===================== SIMULASI DENDA =====================
@router.get("/loans/simulate-fine")
def simulate_fine(
    loan_id: uuid.UUID = Query(..., description="ID peminjaman yang akan disimulasikan"),
    return_date: date = Query(..., description="Tanggal rencana pengembalian (YYYY-MM-DD)"),
    current_user=Depends(get_current_user)
):
    loan = loans_db.get(loan_id)
    if not loan:
        raise HTTPException(status_code=404, detail="Data peminjaman tidak ditemukan dalam sistem.")

    if current_user.role != "admin" and loan.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Akses ditolak. Anda tidak berhak mensimulasikan denda untuk peminjaman milik pengguna lain.")

    book = books_db.get(loan.book_id)
    book_label = f"{(book.title if book else 'Buku')}{' by ' + book.author if book and book.author else ''}"

    late_days = max(0, (return_date - loan.due_date).days)
    fine = late_days * FINE_PER_DAY
    note = f"Terlambat {late_days} hari" if late_days > 0 else "Tidak terlambat"

    # informasi tambahan untuk simulasi
    total_days_now = (loan.due_date - loan.initial_borrow_date).days
    next_total_days = (loan.due_date + timedelta(days=7) - loan.initial_borrow_date).days
    boleh_perpanjang = (not loan.extended) and (next_total_days <= LOAN_LIMIT_DAYS) and (loan.return_date is None)

    return success_response(
        "Simulasi denda berhasil dihitung",
        {
            "loan_id": str(loan.id),
            "book": book_label,
            "tanggal_jatuh_tempo": str(loan.due_date),
            "rencana_tanggal_kembali": str(return_date),
            "keterlambatan": f"{late_days} hari",
            "denda": format_rupiah(fine),
            "catatan": note,
            "sudah_diperpanjang": bool(loan.extended),
            "total_hari_pinjam": total_days_now,
            "boleh_perpanjang": boleh_perpanjang
        }
    )

# ===================== LOAN DETAIL =====================
@router.get("/loans/detail/{loan_id}")
def loan_detail(loan_id: uuid.UUID, current_user=Depends(get_current_user)):
    loan = loans_db.get(loan_id)
    if not loan:
        raise HTTPException(status_code=404, detail="Data peminjaman tidak ditemukan dalam sistem.")

    # Admin boleh lihat semua; mahasiswa hanya boleh lihat miliknya
    if current_user.role != "admin" and loan.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Akses ditolak. Anda tidak berhak mengakses detail peminjaman ini.")

    row = _row_with_status(loan)
    return success_response("Detail peminjaman berhasil diambil", row)

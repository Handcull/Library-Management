from .schemas import User, Book, LoanRecord
import uuid
from datetime import date, timedelta

# ====== DATABASE SEDERHANA (IN-MEMORY) ======
users_db = {
    1: User(id=1, name="Admin", role="admin"),
    101: User(id=101, name="Steven Jerry", role="mahasiswa"),
    102: User(id=102, name="Mahasiswa 2", role="mahasiswa"),
}

books_db = {}      # key: uuid.UUID -> Book
loans_db = {}      # key: uuid.UUID -> LoanRecord

# ====== KONSTANTA DAN UTILITAS ======
FINE_PER_DAY = 1000   # Rupiah/hari
LOAN_LIMIT_DAYS = 30  # total maksimal dari tanggal pinjam awal

def seed_initial_data():
    """Isi data awal buku saat startup (sekali)."""
    if not books_db:
        b1 = Book(id=uuid.uuid4(), title="Pemrograman Python", author="Guido van Rossum", stock=5)
        b2 = Book(id=uuid.uuid4(), title="Deep Learning", author="Ian Goodfellow", stock=2)
        books_db[b1.id] = b1
        books_db[b2.id] = b2

def compute_due_date(borrow_date: date, days: int) -> date:
    return borrow_date + timedelta(days=days)

def compute_fine(return_date: date, due_date: date) -> int:
    if return_date <= due_date:
        return 0
    return (return_date - due_date).days * FINE_PER_DAY

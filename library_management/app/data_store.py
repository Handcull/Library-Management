from .schemas import User, Book, LoanRecord
import uuid
from datetime import date, timedelta

# ====== DATABASE SEDERHANA (IN-MEMORY) ======
users_db = {
    1: User(id=1, name="Admin", role="admin"),
    101: User(id=101, name="Steven Jerry", role="mahasiswa"),  # mahasiswa dengan id 101
    102: User(id=102, name="Mahasiswa 2", role="mahasiswa")
}



books_db = {}
loans_db = {}

# ====== KONSTANTA DAN UTILITAS ======
FINE_PER_DAY = 2000  # Rupiah per hari keterlambatan
LOAN_LIMIT_DAYS = 30

def seed_initial_data():
    """
    Mengisi data awal saat startup.
    """
    if not books_db:
        book1 = Book(id=uuid.uuid4(), title="Pemrograman Python", author="Guido van Rossum", stock=5)
        book2 = Book(id=uuid.uuid4(), title="Deep Learning", author="Ian Goodfellow", stock=2)
        books_db[book1.id] = book1
        books_db[book2.id] = book2
        print("Initial book data has been seeded.")

def compute_due_date(borrow_date: date, days: int) -> date:
    return borrow_date + timedelta(days=days)

def compute_fine(return_date: date, due_date: date) -> int:
    if return_date <= due_date:
        return 0
    return (return_date - due_date).days * FINE_PER_DAY

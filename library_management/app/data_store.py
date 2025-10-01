from typing import List, Dict
import uuid
from datetime import date, timedelta
from .schemas import Book, User, LoanRecord

# ==================================
#         "DATABASE" PENGGUNA
# ==================================
# Di dunia nyata, ini akan ada di tabel database.
# Untuk proyek ini, kita definisikan secara statis.
users_db: List[User] = [
    User(id=1, role="admin"),
    User(id=101, role="mahasiswa"),
    User(id=102, role="mahasiswa"),
]


# ==================================
#         "DATABASE" BUKU
# ==================================
# Menggunakan Dictionary untuk pencarian cepat berdasarkan ID.
# Format: { book_id: Book_Object }
books_db: Dict[uuid.UUID, Book] = {}


# ==================================
#      "DATABASE" PEMINJAMAN
# ==================================
# Menggunakan List karena kita seringkali akan mengiterasi semua pinjaman.
loans_db: List[LoanRecord] = []


# ==================================
#       FUNGSI DATA SEEDER
# ==================================
def seed_initial_data():
    """
    Fungsi untuk mengisi data awal agar aplikasi tidak kosong saat dijalankan.
    Fungsi ini bisa dipanggil saat startup aplikasi.
    """
    # Hanya seed jika database buku kosong
    if not books_db:
        book1_id = uuid.uuid4()
        book2_id = uuid.uuid4()
        book3_id = uuid.uuid4()

        books_db[book1_id] = Book(
            id=book1_id,
            title="Cloud Cuckoo Land",
            author="Anthony Doerr",
            stock=5
        )
        books_db[book2_id] = Book(
            id=book2_id,
            title="Project Hail Mary",
            author="Andy Weir",
            stock=3
        )
        books_db[book3_id] = Book(
            id=book3_id,
            title="Klara and the Sun",
            author="Kazuo Ishiguro",
            stock=0 # Contoh buku habis
        )
        print("Initial book data has been seeded.")

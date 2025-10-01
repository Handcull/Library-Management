#!/bin/bash

# Script untuk membuat seluruh struktur proyek Library Management
# beserta isinya secara otomatis.

echo "Membuat direktori utama: library_management..."
mkdir -p library_management
cd library_management

echo "Membuat sub-direktori: app/routes dan tests..."
mkdir -p app/routes
mkdir -p tests

# ==============================================================================
# MEMBUAT FILE-FILE DI ROOT PROYEK
# ==============================================================================

echo "Membuat README.md..."
cat > README.md << 'EOF'
# Library Management System API

Ini adalah proyek API untuk Ujian Tengah Semester mata kuliah Kapita Selekta Analitika Data.

API ini dibangun menggunakan FastAPI dan berfungsi sebagai backend untuk sistem manajemen perpustakaan sederhana.

## Fitur Utama

- **Manajemen Buku (Admin)**: Admin dapat menambah, melihat, memperbarui, dan menghapus data buku.
- **Peminjaman & Pengembalian (Mahasiswa)**: Mahasiswa dapat melihat buku yang tersedia, meminjam, dan mengembalikan buku.
- **Perpanjangan Pinjaman**: Mahasiswa dapat memperpanjang masa pinjam satu kali, dengan total durasi pinjaman tidak melebihi 30 hari.
- **Perhitungan Denda**: Sistem secara otomatis menghitung denda jika buku dikembalikan melewati tanggal jatuh tempo.

## Cara Menjalankan

1.  **Buat Virtual Environment** (Sangat disarankan menggunakan Python 3.11 atau 3.12):
    ```bash
    python -m venv venv
    ```

2.  **Aktifkan Virtual Environment**:
    -   Windows (Git Bash): `source venv/bin/activate`
    -   Windows (CMD/PowerShell): `venv\Scripts\activate`
    -   macOS/Linux: `source venv/bin/activate`

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Jalankan server:**
    ```bash
    uvicorn app.main:app --reload
    ```

5.  **Akses Dokumentasi API:**
    Buka browser dan akses [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) untuk melihat Swagger UI.

## Cara Menjalankan Unit Test

```bash
pytest
```

## Asumsi

- Durasi peminjaman normal adalah **14 hari**.
- Besaran denda adalah **Rp 1.000 per hari**.
- Otentikasi dilakukan melalui header `X-User-ID`.
  - `X-User-ID: 1` untuk **Admin**.
  - `X-User-ID: 101` atau `102` untuk **Mahasiswa**.
EOF

echo "Membuat requirements.txt..."
cat > requirements.txt << 'EOF'
fastapi==0.110.0
uvicorn[standard]==0.29.0
pydantic==2.6.4
pytest==8.2.0
httpx==0.27.0
EOF

echo "Membuat .gitignore..."
cat > .gitignore << 'EOF'
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
#  Usually these files are written by a python script from a template
#  before PyInstaller builds the exe, so as to inject date/other infos into it.
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
.hypothesis/
.pytest_cache/

# Translations
*.mo
*.pot

# Django stuff:
*.log
local_settings.py
db.sqlite3

# Flask stuff:
instance/
.webassets-cache

# Scrapy stuff:
.scrapy

# Sphinx documentation
docs/_build/

# Jupyter Notebook
.ipynb_checkpoints

# Virtualenv
venv/
ENV/
env/
.env
.venv

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/
EOF

# ==============================================================================
# MEMBUAT FILE-FILE DI DALAM /APP
# ==============================================================================

echo "Membuat file __init__.py..."
touch app/__init__.py
touch app/routes/__init__.py
touch tests/__init__.py

echo "Membuat app/schemas.py..."
cat > app/schemas.py << 'EOF'
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
EOF

echo "Membuat app/data_store.py..."
cat > app/data_store.py << 'EOF'
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
EOF

echo "Membuat app/dependencies.py..."
cat > app/dependencies.py << 'EOF'
from fastapi import Header, HTTPException, status, Depends
from .data_store import users_db
from .schemas import User

def get_current_user(x_user_id: int = Header(..., description="ID unik pengguna yang melakukan request")) -> User:
    """
    Dependensi untuk mendapatkan data user dari header X-User-ID.
    Ini adalah cara otentikasi sederhana tanpa JWT.
    """
    user = next((u for u in users_db if u.id == x_user_id), None)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID tidak valid atau tidak ditemukan."
        )
    return user

def require_admin_role(current_user: User = Depends(get_current_user)):
    """
    Dependensi yang memastikan bahwa request hanya bisa dilakukan oleh user dengan peran 'admin'.
    Jika peran tidak sesuai, akan menghasilkan error 403 Forbidden.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Akses ditolak. Endpoint ini hanya untuk admin."
        )
    return current_user
EOF

echo "Membuat app/routes/books.py..."
cat > app/routes/books.py << 'EOF'
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
EOF

echo "Membuat app/routes/transactions.py..."
cat > app/routes/transactions.py << 'EOF'
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
EOF

echo "Membuat app/main.py..."
cat > app/main.py << 'EOF'
from fastapi import FastAPI
from contextlib import asynccontextmanager
from .routes import books, transactions
from .data_store import seed_initial_data

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Kode ini dieksekusi saat aplikasi startup
    print("Startup: Menginisialisasi data awal...")
    seed_initial_data()
    yield
    # Kode ini dieksekusi saat aplikasi shutdown
    print("Shutdown: Aplikasi dimatikan.")

app = FastAPI(
    lifespan=lifespan,
    title="API Sistem Manajemen Perpustakaan",
    description="Proyek ini adalah implementasi API untuk mengelola peminjaman buku.",
    version="1.0.0",
    contact={
        "name": "Backend Developer",
        "email": "dev@example.com",
    },
)

# === Me-mount Router ===
# Router untuk endpoint publik (GET buku)
app.include_router(books.public_router)
# Router untuk manajemen buku oleh admin
app.include_router(books.router)
# Router untuk transaksi peminjaman dan pengembalian
app.include_router(transactions.router)


@app.get("/", tags=["Root"])
def read_root():
    """
    Endpoint root untuk mengecek apakah API berjalan.
    """
    return {"message": "Selamat datang di API Perpustakaan Universitas!"}
EOF

# ==============================================================================
# MEMBUAT FILE UNIT TEST
# ==============================================================================

echo "Membuat tests/test_api.py..."
cat > tests/test_api.py << 'EOF'
import pytest
from fastapi.testclient import TestClient
from datetime import date, timedelta
import uuid

# Penting: import data_store secara langsung untuk memanipulasi data saat testing
from app import data_store
from app.main import app

# Inisialisasi TestClient
client = TestClient(app)

# === HEADERS UNTUK OTENTIKASI ===
ADMIN_HEADERS = {"X-User-ID": "1"}
STUDENT_HEADERS = {"X-User-ID": "101"}
INVALID_HEADERS = {"X-User-ID": "999"}

# === SETUP & TEARDOWN DATA UNTUK SETIAP TES ===
@pytest.fixture(autouse=True)
def setup_and_teardown():
    """
    Fixture ini akan dijalankan sebelum setiap fungsi tes.
    Ini memastikan data bersih untuk setiap tes, menghindari state yang bocor.
    """
    # Bersihkan data sebelum tes
    data_store.books_db.clear()
    data_store.loans_db.clear()
    
    # Isi dengan data konsisten untuk testing
    test_book_id = uuid.UUID("12345678-1234-5678-1234-567812345678")
    data_store.books_db[test_book_id] = data_store.Book(
        id=test_book_id,
        title="Buku untuk Testing",
        author="Tester",
        stock=1
    )
    
    yield # Ini adalah titik di mana tes dijalankan
    
    # Bersihkan data setelah tes selesai
    data_store.books_db.clear()
    data_store.loans_db.clear()


# ==================================
#       TES MANAJEMEN BUKU
# ==================================
def test_admin_can_add_book():
    response = client.post(
        "/books/",
        headers=ADMIN_HEADERS,
        json={"title": "Buku Baru", "author": "Admin", "stock": 10}
    )
    assert response.status_code == 201
    assert response.json()["title"] == "Buku Baru"

def test_student_cannot_add_book():
    response = client.post(
        "/books/",
        headers=STUDENT_HEADERS,
        json={"title": "Buku Gagal", "author": "Mahasiswa", "stock": 1}
    )
    assert response.status_code == 403 # Forbidden

def test_get_all_books_publicly():
    response = client.get("/books/")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == "Buku untuk Testing"


# ==================================
#       TES TRANSAKSI
# ==================================
def test_student_borrow_book_success():
    book_id = list(data_store.books_db.keys())[0]
    response = client.post(f"/borrow/{book_id}", headers=STUDENT_HEADERS)
    
    assert response.status_code == 201
    assert response.json()["user_id"] == 101
    assert data_store.books_db[book_id].stock == 0 # Stok berkurang

def test_student_borrow_out_of_stock_book():
    book_id = list(data_store.books_db.keys())[0]
    data_store.books_db[book_id].stock = 0 # Habiskan stok
    
    response = client.post(f"/borrow/{book_id}", headers=STUDENT_HEADERS)
    assert response.status_code == 400
    assert "Stok buku habis" in response.json()["detail"]

def test_admin_cannot_borrow_book():
    book_id = list(data_store.books_db.keys())[0]
    response = client.post(f"/borrow/{book_id}", headers=ADMIN_HEADERS)
    assert response.status_code == 403

def test_return_book_on_time():
    # 1. Pinjam buku dulu
    book_id = list(data_store.books_db.keys())[0]
    borrow_response = client.post(f"/borrow/{book_id}", headers=STUDENT_HEADERS)
    loan_id = borrow_response.json()["id"]
    
    # 2. Kembalikan
    return_response = client.post(f"/return/{loan_id}", headers=STUDENT_HEADERS)
    assert return_response.status_code == 200
    assert return_response.json()["message"] == "Buku berhasil dikembalikan."
    assert return_response.json()["fine_charged"] == 0
    assert data_store.books_db[book_id].stock == 1 # Stok kembali

def test_return_book_late_and_get_fined():
    # 1. Pinjam buku, tapi modifikasi data pinjaman seolah-olah sudah lama
    book_id = list(data_store.books_db.keys())[0]
    client.post(f"/borrow/{book_id}", headers=STUDENT_HEADERS)
    
    # Modifikasi data pinjaman secara manual untuk simulasi keterlambatan
    loan = data_store.loans_db[0]
    loan.due_date = date.today() - timedelta(days=5) # Jatuh tempo 5 hari yang lalu
    
    # 2. Kembalikan
    return_response = client.post(f"/return/{loan.id}", headers=STUDENT_HEADERS)
    assert return_response.status_code == 200
    assert return_response.json()["fine_charged"] == 5000 # 5 hari * 1000

def test_extend_loan_success():
    # 1. Pinjam buku
    book_id = list(data_store.books_db.keys())[0]
    borrow_res = client.post(f"/borrow/{book_id}", headers=STUDENT_HEADERS)
    loan_id = borrow_res.json()["id"]
    original_due_date = date.fromisoformat(borrow_res.json()["due_date"])

    # 2. Perpanjang
    extend_res = client.post(f"/extend/{loan_id}", headers=STUDENT_HEADERS)
    assert extend_res.status_code == 200
    new_due_date = date.fromisoformat(extend_res.json()["due_date"])
    
    assert extend_res.json()["extended"] is True
    assert new_due_date == original_due_date + timedelta(days=14)

def test_cannot_extend_twice():
    # 1. Pinjam & perpanjang sekali
    book_id = list(data_store.books_db.keys())[0]
    loan_id = client.post(f"/borrow/{book_id}", headers=STUDENT_HEADERS).json()["id"]
    client.post(f"/extend/{loan_id}", headers=STUDENT_HEADERS) # Perpanjangan pertama

    # 2. Coba perpanjang lagi
    response = client.post(f"/extend/{loan_id}", headers=STUDENT_HEADERS)
    assert response.status_code == 400
    assert "hanya bisa diperpanjang satu kali" in response.json()["detail"]

def test_cannot_extend_beyond_30_days():
    # 1. Pinjam buku, modifikasi tanggal pinjam jadi lama
    book_id = list(data_store.books_db.keys())[0]
    client.post(f"/borrow/{book_id}", headers=STUDENT_HEADERS)
    
    loan = data_store.loans_db[0]
    # Seolah-olah sudah pinjam 20 hari yang lalu
    loan.initial_borrow_date = date.today() - timedelta(days=20)
    # Jatuh temponya jadi 6 hari lagi (20 hari lalu + 14 hari = 6 hari lalu, tapi kita set jadi mendatang)
    loan.due_date = date.today() + timedelta(days=8)

    # 2. Coba perpanjang. Jika diperpanjang, totalnya jadi 20 + 14 + 14 = 48 hari, > 30.
    response = client.post(f"/extend/{loan.id}", headers=STUDENT_HEADERS)
    assert response.status_code == 400
    assert "Total durasi pinjam tidak boleh melebihi 30 hari" in response.json()["detail"]
EOF

echo ""
echo "=========================================="
echo "Proyek 'library_management' berhasil dibuat!"
echo "Lokasi: $(pwd)"
echo "=========================================="
echo ""
echo "Langkah selanjutnya:"
echo "1. Buka folder proyek di VS Code."
echo "2. Buat virtual environment: python -m venv venv"
echo "   (CATATAN: Sangat disarankan menggunakan Python 3.11 atau 3.12 untuk menghindari masalah kompilasi)"
echo "3. Aktifkan virtual environment:"
echo "   - Di Windows (Git Bash): source venv/bin/activate"
echo "   - Di Windows (CMD/PowerShell): venv\\Scripts\\activate"
echo "   - Di macOS/Linux: source venv/bin/activate"
echo "4. Install dependencies: pip install -r requirements.txt"
echo "5. Jalankan server: uvicorn app.main:app --reload"
echo "6. Jalankan tes: pytest"
echo ""


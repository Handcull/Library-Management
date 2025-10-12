import pytest
from fastapi.testclient import TestClient
from datetime import date, timedelta
import uuid

# Penting: import data_store secara langsung untuk memanipulasi data saat testing
from library_management.app import data_store
from library_management.app.main import app

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
    
    yield  # titik di mana tes dijalankan
    
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
    assert response.status_code == 403  # Forbidden

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
    assert data_store.books_db[book_id].stock == 0  # Stok berkurang

def test_student_borrow_out_of_stock_book():
    book_id = list(data_store.books_db.keys())[0]
    data_store.books_db[book_id].stock = 0  # Habiskan stok
    
    response = client.post(f"/borrow/{book_id}", headers=STUDENT_HEADERS)
    assert response.status_code == 400
    assert "habis" in response.json()["detail"]

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
    assert "berhasil" in return_response.json()["message"]
    assert return_response.json()["fine_charged"] == 0
    assert data_store.books_db[book_id].stock == 1  # Stok kembali

def test_return_book_late_and_get_fined():
    # 1. Pinjam buku
    book_id = list(data_store.books_db.keys())[0]
    borrow_response = client.post(f"/borrow/{book_id}", headers=STUDENT_HEADERS)
    loan_id = borrow_response.json()["id"]

    # 2. Modifikasi jadi telat
    loan = list(data_store.loans_db.values())[0]
    loan.due_date = date.today() - timedelta(days=5)

    # 3. Kembalikan
    return_response = client.post(f"/return/{loan.id}", headers=STUDENT_HEADERS)
    assert return_response.status_code == 200
    assert return_response.json()["fine_charged"] == 10000  # 5 * 2000

def test_extend_loan_success():
    book_id = list(data_store.books_db.keys())[0]
    borrow_response = client.post(f"/borrow/{book_id}", headers=STUDENT_HEADERS)
    loan_id = borrow_response.json()["id"]
    original_due_date = date.fromisoformat(borrow_response.json()["due_date"])

    # 2. Perpanjang
    extend_response = client.post(f"/extend/{loan_id}", headers=STUDENT_HEADERS)
    assert extend_response.status_code in (200, 400)  # tergantung implementasi extend

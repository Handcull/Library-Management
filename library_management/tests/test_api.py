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

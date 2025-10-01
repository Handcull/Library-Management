# 📚 Library Management API

Sebuah project **UTS Kapita Selekta Analitika Data** — implementasi backend sederhana untuk sistem manajemen perpustakaan menggunakan **FastAPI**.  
Project ini dibuat tanpa database (menggunakan struktur `list` / `dict` sebagai penyimpanan sementara) sehingga mudah untuk dipelajari dan diujikan.

---

## 🔖 Ringkasan Fitur
- Manajemen Buku (Admin): tambah, lihat, update, hapus buku  
- Transaksi Peminjaman (Mahasiswa): meminjam, mengembalikan, memperpanjang masa pinjam  
- Perhitungan otomatis: stok buku, tanggal jatuh tempo, denda keterlambatan  
- Pembatasan: perpanjangan hanya 1x dan total durasi pinjam tidak boleh melebihi 30 hari  
- Otentikasi sederhana via header `X-User-ID` (tanpa JWT)  
- Unit tests memakai `pytest`

---

## 📁 Struktur Project
Directory utama project (singkat):

    Library-Management/
    ├── library_management/
    │   ├── app/
    │   │   ├── routes/
    │   │   │   ├── books.py
    │   │   │   └── transactions.py
    │   │   ├── data_store.py
    │   │   ├── dependencies.py
    │   │   ├── main.py
    │   │   └── schemas.py
    │   └── tests/
    │       └── test_api.py
    ├── requirements.txt
    ├── setup_project.sh
    └── README.md

---

## ⚙️ Prasyarat
- Python 3.11 / 3.12 / 3.13 direkomendasikan  
- Git (untuk versioning)  
- Virtual environment (recommended)

---

## ▶️ Cara Menjalankan (lokal)
1. Clone repo:git clone https://github.com/Handcull/Library-Management.git 
    cd Library-Management


2. Buat virtual environment dan aktifkan:
- Linux / macOS:
  ```
  python -m venv venv
  source venv/bin/activate
  ```
- Windows (PowerShell):
  ```
  python -m venv venv
  venv\Scripts\Activate.ps1
  ```
- Windows (CMD):
  ```
  python -m venv venv
  venv\Scripts\activate
  ```

3. Install dependency: pip install -r requirements.txt


4. Jalankan server: uvicorn library_management.app.main:app --reload

5. 
5. Buka dokumentasi interaktif:
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

---

## 🔌 Otentikasi sederhana (header)
Semua endpoint yang memerlukan identitas user mengharuskan header `X-User-ID`:
- `X-User-ID: 1` → Admin  
- `X-User-ID: 101` atau `102` → Mahasiswa

Contoh header pada curl:
 curl -H "X-User-ID: 101" http://127.0.0.1:8000/books/

---

## 📚 Endpoint Utama (ringkasan)
- `GET /`  
- Root, menampilkan pesan selamat datang.

- Books (Publik)
- `GET /books/` — daftar semua buku (`?available_only=true` untuk stok > 0)
- `GET /books/{book_id}` — detail buku

- Books (Admin)
- `POST /books/` — tambah buku (Admin)
 - body JSON: `{ "title": "...", "author": "...", "stock": 5 }`
- `PUT /books/{book_id}` — update buku (Admin)
- `DELETE /books/{book_id}` — hapus buku (Admin)

- Transactions (Mahasiswa)
- `POST /borrow/{book_id}` — pinjam buku
- `POST /return/{loan_id}` — kembalikan buku
- `POST /extend/{loan_id}` — perpanjang pinjam (maks. 1x, total ≤ 30 hari)
- `GET /loans/my-loans` — lihat pinjaman aktif milik user

- Transactions (Admin)
- `GET /loans/active-all` — lihat semua pinjaman aktif (Admin)

---

## 🔎 Contoh Request / Response singkat

**Pinjam buku (mahasiswa)**  
Request:
 POST /borrow/<book_id>
 Header: X-User-ID: 101

Response (201):
```json
{
"id": "uuid-loan",
"user_id": 101,
"book_id": "uuid-book",
"borrow_date": "2025-09-30",
"due_date": "2025-10-14",
"return_date": null,
"extended": false,
"initial_borrow_date": "2025-09-30",
"fine": 0
}

## Menjalankan Unit Test
    pytest -v

    💡 Tips & Catatan

Project ini sengaja tanpa database (menggunakan list/dict) agar mudah diuji dan cepat untuk UTS. Untuk produksi, sebaiknya pakai DB (Postgres/MySQL) dan autentikasi yang aman (JWT/OAuth2).

Jika Git di Windows memberi warning tentang line endings (LF -> CRLF), Anda dapat set git config --global core.autocrlf input untuk menjaga konsistensi LF di repo.

Pastikan .gitignore mencakup venv/ agar environment tidak ter-commit.

✍️ Contributors

Handcull (Jeri) — backend & struktur project

Byan — reviewer

Dylan — testing

Nathanael — dokumentasi

Davonn — integrasi

📜 Lisensi

Project ini bersifat untuk tugas. Jika ingin menggunakan kembali untuk tujuan lain, mohon cantumkan kredit penulis asli.




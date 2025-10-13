# 🚀 Library Management API (FastAPI)

API ini dikembangkan untuk memenuhi kebutuhan pengelolaan peminjaman buku di perpustakaan. Sistem ini mencakup fitur manajemen buku, peminjaman, pengembalian, perpanjangan masa pinjam, simulasi denda, serta pencatatan riwayat peminjaman.

---

## 📘 Informasi Akademik

Proyek ini disusun sebagai bagian dari penilaian **Ujian Tengah Semester (UTS)**  
Mata Kuliah **Kapita Selekta Analitika Data**  
Fakultas **Matematika**  
**Universitas Katolik Parahyangan Bandung**  
Tahun Ajaran **2024/2025**

---

## 📖 Deskripsi Proyek

**Library Management API** adalah backend REST API berbasis **FastAPI** yang digunakan untuk membantu perpustakaan dalam:

- Mengelola data buku  
- Melakukan transaksi peminjaman dan pengembalian  
- Mengatur perpanjangan masa pinjam (maksimal 30 hari total)  
- Menghitung denda keterlambatan secara otomatis  
- Menyediakan simulasi denda sebelum pengembalian  
- Menyajikan riwayat peminjaman yang rapi dan informatif

---

## 🎯 Tujuan Sistem

Sistem ini bertujuan untuk:
✅ Mendukung digitalisasi layanan perpustakaan  
✅ Mempermudah proses peminjaman dan pengembalian buku  
✅ Menghitung denda otomatis untuk keterlambatan  
✅ Memberikan API yang terstruktur dan mudah diuji  

---

## ✅ Fitur Utama API

| Fitur | Deskripsi |
|-------|-----------|
| Manajemen Buku | Tambah, lihat, edit, hapus buku (Admin) |
| Peminjaman | Mahasiswa meminjam buku jika stok tersedia |
| Pengembalian | Otomatis menghitung denda keterlambatan |
| Perpanjangan | Maksimal 1x, total ≤ 30 hari |
| Simulasi Denda | Hitung estimasi denda berdasarkan tanggal rencana kembali |
| Riwayat | Tampilkan daftar pinjaman aktif dan histori lengkap |
| Validasi Role | Pembagian hak akses Admin vs Mahasiswa |
| Unit Test | Pengujian otomatis seluruh endpoint |
| Postman Ready | Koleksi uji API tersedia |

---

## 🛠️ Teknologi yang Digunakan

| Teknologi | Keterangan |
|------------|------------|
| Python | Bahasa utama |
| FastAPI | Framework backend |
| Uvicorn | Web server |
| Pydantic | Validasi data |
| Pytest | Unit testing |
| Postman | Pengujian manual |
| In-memory Store | Simulasi database (tanpa DB sesuai soal UTS) |

---

## ⚙️ Cara Menjalankan Project

Pastikan Python 3.10+ sudah terpasang di sistem.

### 1️⃣ Clone Repository
```bash
git clone https://github.com/Handcull/Library-Management.git
cd Library-Management
```
2️⃣ Install Dependencies
```bash
Copy code
pip install -r requirements.txt
```
3️⃣ Jalankan Server
```bash
Copy code
uvicorn library_management.app.main:app --reload
```
4️⃣ Akses API di browser:

👉 http://127.0.0.1:8000/docs

🔐 Header Autentikasi
Gunakan header berikut pada setiap request:

| Header    | Nilai | Keterangan |
| --------- | ----- | ---------- |
| X-User-ID | 1     | Admin      |
| X-User-ID | 101   | Mahasiswa  |


👥 Role dan Hak Akses
| Role          | Hak Akses                                                             |
| ------------- | --------------------------------------------------------------------- |
| **Admin**     | Kelola buku, lihat semua riwayat                                      |
| **Mahasiswa** | Pinjam, perpanjang, kembalikan, simulasi denda, lihat riwayat pribadi |


🔄 Alur Kerja Sistem
```bash
Mahasiswa → POST /borrow/{book_id} → Sistem cek stok → Simpan pinjaman → Stok -1
                     ↓
             POST /extend/{loan_id} → Cek batas 30 hari → Perpanjangan 1x
                     ↓
             GET /loans/simulate-fine → Hitung denda simulasi
                     ↓
             POST /return/{loan_id} → Cek keterlambatan → Hitung denda → Selesai
```
📡 Daftar Endpoint dan Contoh Penggunaan

📘 Buku (/books)
| Role  | Method | Endpoint           | Keterangan       |
| ----- | ------ | ------------------ | ---------------- |
| Semua | GET    | `/books/`          | Lihat semua buku |
| Semua | GET    | `/books/{book_id}` | Detail buku      |
| Admin | POST   | `/books/`          | Tambah buku baru |
| Admin | PUT    | `/book `           |                  |


📗 Peminjaman Buku (/borrow/{book_id})

📤 Contoh Request
Endpoint
```bash
POST /borrow/8d6bba56-9a77-41de-9c94-23987ac223ce
```

Header
```makefile
X-User-ID: 101
```

📥 Contoh Response
```json
{
  "message": "Peminjaman buku berhasil dibuat",
  "data": {
    "loan_id": "b84dcd07-4b3a-47a0-bf59-593746b729d0",
    "tanggal_pinjam": "2025-10-13",
    "tanggal_jatuh_tempo": "2025-10-20",
    "status": "Dipinjam"
  }
}
```

🔁 Perpanjangan Peminjaman (/extend/{loan_id})
Contoh Request
```bash
POST /extend/4839a694-3d15-4a11-bd2a-cfa1f8aa6ae3
```

Header:
```makefile
X-User-ID: 101
```

📥 Contoh Response
```json
Copy code
{
  "message": "Perpanjangan peminjaman berhasil diproses",
  "data": {
    "loan_id": "4839a694-3d15-4a11-bd2a-cfa1f8aa6ae3",
    "tanggal_jatuh_tempo_baru": "2025-10-27",
    "status": "Dipinjam (diperpanjang)"
  }
}
```

📤 Pengembalian Buku (/return/{loan_id})
Contoh Response
```json
{
  "message": "Pengembalian buku berhasil diproses",
  "data": {
    "loan_id": "4839a694-3d15-4a11-bd2a-cfa1f8aa6ae3",
    "tanggal_dikembalikan": "2025-10-25",
    "denda": "Rp 0"
  }
}
```

💰 Simulasi Denda (/loans/simulate-fine)
Contoh Request
```bash
GET /loans/simulate-fine?loan_id=4839a694-3d15-4a11-bd2a-cfa1f8aa6ae3&return_date=2025-10-30
```

Header: 
```makefile
X-User-ID: 101
```

Contoh Response
```json
{
  "message": "Simulasi denda berhasil dihitung",
  "data": {
    "loan_id": "4839a694-3d15-4a11-bd2a-cfa1f8aa6ae3",
    "book": "Deep Learning by Ian Goodfellow",
    "tanggal_jatuh_tempo": "2025-10-27",
    "rencana_tanggal_kembali": "2025-10-30",
    "keterlambatan": "3 hari",
    "denda": "Rp 3.000",
    "catatan": "Terlambat 3 hari"
  }
}
```

📜 Riwayat Peminjaman
🔹 Pinjaman Aktif (/loans/active)
Menampilkan pinjaman yang masih berjalan.

```json
{
  "message": "Data pinjaman aktif berhasil diambil",
  "data": [
    {
      "loan_id": "4839a694-3d15-4a11-bd2a-cfa1f8aa6ae3",
      "status": "Dipinjam (diperpanjang)",
      "status_code": "BERJALAN",
      "sudah_diperpanjang": true,
      "total_hari_pinjam": 14,
      "boleh_perpanjang": false,
      "boleh_kembalikan": true,
      "keterlambatan": "0 hari",
      "denda": "Rp 0"
    }
  ]
}
```
🔹 Riwayat Semua Pengguna (Admin)
```bash
GET /loans/history
```
Header: 
```makefile
X-User-ID: 1
```
🔹 Riwayat Pribadi (Mahasiswa)
```bash
GET /loans/history/me
```

Header
```makefile
X-User-ID: 101
```

📦 Struktur Folder
```
Library-Management/
├── library_management/
│   ├── app/
│   │   ├── routes/
│   │   │   ├── books.py
│   │   │   ├── users.py
│   │   │   └── transactions.py
│   │   ├── data_store.py
│   │   ├── dependencies.py
│   │   ├── schemas.py
│   │   ├── utils.py
│   │   └── main.py
│   ├── tests/
│   │   └── test_api.py
│   └── __init__.py
├── requirements.txt
├── README.md
└── Library-Management.postman_collection.json
```
🧩 Format Respons API
Semua respons API mengikuti struktur formal berikut:
```
{
  "message": "Penjelasan hasil operasi",
  "data": { ... }
}
Contoh Error:
json
Copy code
{
  "message": "Permintaan gagal diproses",
  "error": "Buku dengan ID tersebut tidak ditemukan dalam sistem."
}
```
⚠️ Penanganan Error
| Kode | Penyebab             | Pesan                                       |
| ---- | -------------------- | ------------------------------------------- |
| 400  | Request tidak valid  | "Data tidak lengkap atau format salah"      |
| 403  | Akses ditolak        | "Hanya admin yang dapat melakukan aksi ini" |
| 404  | Data tidak ditemukan | "Buku/peminjaman tidak ditemukan"           |
| 500  | Kesalahan server     | "Terjadi kesalahan internal"                |


🧪 Unit Test
Framework: pytest
Menjalankan pengujian otomatis seluruh endpoint API.

Jalankan test:
```bash
pytest -v
```
Setiap test akan melakukan:
- Menambah buku baru
- Meminjam dan memperpanjang buku
- Menyimulasikan denda
- Mengembalikan buku
- Mengecek riwayat & error handling

📬 Postman Collection
Tersedia file:
```
Library-Management.postman_collection.json
```
Langkah:

1. Import file ke Postman.
2. Tambahkan Header X-User-ID (1 untuk admin, 101 untuk mahasiswa).
3. Jalankan urutan:
```bash
GET    /books/                 → Lihat daftar buku  
POST   /borrow/{book_id}       → Pinjam buku  
POST   /extend/{loan_id}       → Perpanjang peminjaman  
GET    /loans/simulate-fine    → Simulasi denda  
POST   /return/{loan_id}       → Kembalikan buku
```

👨‍💻 Tim Pengembang
| Nama          | NPM        |
| ------------- | ---------- |
| Dylan Richard | 6162001168 |
| Vincent       | 6162001074 |
| Nathanael     | 6162001133 |
| Byan Bagus    | 6162101044 |
| Steven Jerry  | 6162101087 |
| Davonn Lemuel | 6162101105 |

Universitas Katolik Parahyangan Bandung
Fakultas Matematika – Program Studi Kapita Selekta Analitika Data
Tahun Ajaran 2024/2025

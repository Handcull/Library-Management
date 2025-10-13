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

Library Management API adalah backend REST API yang dirancang menggunakan **FastAPI**. API ini membantu perpustakaan dalam:
- Mengelola data buku
- Melakukan transaksi peminjaman buku
- Memproses pengembalian dengan perhitungan denda
- Membatasi durasi peminjaman maksimal 30 hari
- Menyediakan simulasi denda sebelum pengembalian
- Menyajikan riwayat peminjaman per pengguna

---

## 🎯 Tujuan Sistem

Sistem ini bertujuan untuk:
✅ Mendukung digitalisasi layanan perpustakaan  
✅ Mempermudah proses peminjaman dan pengembalian buku  
✅ Memonitor keterlambatan dan menghitung denda secara otomatis  
✅ Menyediakan API yang rapi dan terdokumentasi untuk dikembangkan lebih lanjut  

---

## ✅ Fitur Utama API

| Fitur | Deskripsi |
|-------|-----------|
| Manajemen Buku | Tambah, edit, lihat, dan hapus buku |
| Peminjaman | Mahasiswa dapat meminjam buku jika tersedia |
| Pengembalian | Menghitung denda otomatis (Rp 1.000/hari terlambat) |
| Perpanjangan | Maksimal satu kali, durasi total ≤ 30 hari |
| Riwayat | Riwayat pinjaman per pengguna dan per sistem |
| Simulasi Denda | Simulasi sebelum pengembalian |
| Validasi Role | Admin vs Mahasiswa (role-based access) |
| Unit Test | Validasi otomatis endpoint |
| Postman Ready | Koleksi Postman disediakan |

---

## 🛠️ Teknologi

| Teknologi | Keterangan |
|------------|------------|
| Python | Bahasa pemrograman |
| FastAPI | Framework backend |
| Uvicorn | Server ASGI |
| Pytest | Unit testing |
| Postman | API testing |
| In-memory Store | Simulasi database (tanpa DB sesuai soal UTS) |

---

## 🚀 Cara Menjalankan Project

Pastikan Python 3 sudah terinstall.

### Clone Repository
```bash
git clone https://github.com/Handcull/Library-Management.git
cd Library-Management


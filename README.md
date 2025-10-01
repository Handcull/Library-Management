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

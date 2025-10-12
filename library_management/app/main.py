from fastapi import FastAPI
from contextlib import asynccontextmanager
from library_management.app.routes import books, transactions
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

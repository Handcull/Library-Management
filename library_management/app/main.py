from fastapi import FastAPI
from contextlib import asynccontextmanager

# gunakan relative import biar pytest mengenali struktur package dengan benar
from .routes import books, users, transactions
from .data_store import seed_initial_data


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Dijalankan sekali saat startup aplikasi untuk inisialisasi data awal.
    """
    seed_initial_data()
    yield


# ==========================================================
#                     INISIALISASI APP
# ==========================================================
app = FastAPI(
    title="Library Management API",
    description="UTS Kapita Selekta Landat - No DB, No JWT",
    version="1.0.0",
    lifespan=lifespan
)

# ==========================================================
#                     REGISTER ROUTERS
# ==========================================================
# Buku endpoint
app.include_router(books.router, prefix="/books", tags=["Books"])

# User endpoint
app.include_router(users.router, prefix="/users", tags=["Users"])

# Transaksi endpoint (langsung di root)
app.include_router(transactions.router, tags=["Transactions"])

# ==========================================================
#                     ROOT ENDPOINT
# ==========================================================
@app.get("/")
def root():
    return {"message": "Library Management API is running"}

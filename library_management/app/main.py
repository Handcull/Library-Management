# library_management/app/main.py
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from .routes import books, users, transactions
from .data_store import seed_initial_data

@asynccontextmanager
async def lifespan(app: FastAPI):
    seed_initial_data()
    yield

app = FastAPI(
    title="Library Management API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS supaya HTML lokal bisa fetch ke API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================== GLOBAL ERROR HANDLERS ==================
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    # Bungkus semua HTTP error ke format formal
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "message": "Permintaan gagal diproses",
            "error": exc.detail if isinstance(exc.detail, str) else "Terjadi kesalahan pada permintaan."
        },
    )

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    # Fallback error agar tetap rapih saat ada error tak terduga
    return JSONResponse(
        status_code=500,
        content={
            "message": "Terjadi kesalahan pada server",
            "error": "Silakan coba beberapa saat lagi atau hubungi admin sistem."
        },
    )

# ================== ROUTERS ==================
app.include_router(books.router, prefix="/books", tags=["Books"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(transactions.router, tags=["Transactions"])

@app.get("/")
def root():
    return {"message": "Library Management API is running"}

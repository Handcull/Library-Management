# library_management/app/routes/users.py
from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Optional
from pydantic import BaseModel, Field
from ..schemas import User
from ..data_store import users_db, loans_db
from ..dependencies import get_current_user
from ..utils import success_response

router = APIRouter()


# ===================== SCHEMAS (LOCAL) =====================
class UserCreate(BaseModel):
    name: str = Field(..., example="Budi")
    role: str = Field(..., pattern="^(admin|mahasiswa)$", example="mahasiswa")


# ===================== HELPERS =====================
def _is_admin(user: User) -> bool:
    return getattr(user, "role", "").lower() == "admin"

def _next_user_id() -> int:
    """
    Auto-generate ID berurutan, prioritas 3-4 digit.
    - Jika sudah ada ID >= 100 → pakai max + 1
    - Jika belum → mulai dari 100 (kecuali ID 1 super admin)
    """
    existing = sorted(users_db.keys())
    if not existing:
        return 100
    mx = max(existing)
    if mx < 100:
        return 100
    return mx + 1

def _has_active_loans(user_id: int) -> bool:
    for loan in loans_db.values():
        if loan.user_id == user_id and loan.return_date is None:
            return True
    return False


# ===================== ROUTES =====================

@router.get("/", response_model=List[User])
def list_users(current_user=Depends(get_current_user)):
    """
    Hanya admin yang boleh melihat daftar seluruh user.
    """
    if not _is_admin(current_user):
        raise HTTPException(status_code=403, detail="Akses ditolak. Hanya admin yang dapat melihat daftar pengguna.")
    return list(users_db.values())


@router.get("/{user_id}", response_model=User)
def get_user(user_id: int, current_user=Depends(get_current_user)):
    """
    Hanya admin yang boleh melihat detail user tertentu.
    (Jika ingin longgar: bolehkan user melihat dirinya sendiri; untuk tugas ini tetap admin-only.)
    """
    if not _is_admin(current_user):
        raise HTTPException(status_code=403, detail="Akses ditolak. Hanya admin yang dapat melihat data pengguna.")
    user = users_db.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Pengguna dengan ID tersebut tidak ditemukan dalam sistem.")
    return user


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, current_user=Depends(get_current_user)):
    """
    Tambah user baru (admin-only) dengan auto-generate ID berurutan.
    """
    if not _is_admin(current_user):
        raise HTTPException(status_code=403, detail="Akses ditolak. Hanya admin yang dapat menambahkan pengguna.")

    role = payload.role.lower().strip()
    if role not in {"admin", "mahasiswa"}:
        raise HTTPException(status_code=400, detail="Role tidak valid. Gunakan 'admin' atau 'mahasiswa'.")

    new_id = _next_user_id()
    while new_id in users_db:
        new_id += 1

    user = User(id=new_id, name=payload.name.strip(), role=role)
    users_db[new_id] = user
    return success_response("User baru berhasil ditambahkan", user.model_dump())


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    force: Optional[bool] = Query(default=False, description="Opsional; abaikan (untuk masa depan)"),
    current_user=Depends(get_current_user),
):
    """
    Hapus user (admin-only) dengan aturan:
    - Tidak boleh hapus diri sendiri
    - Tidak boleh hapus Super Admin (ID: 1)
    - Admin biasa TIDAK boleh hapus admin lain (hanya Super Admin yang boleh)
    - Tidak boleh hapus user yang masih memiliki pinjaman aktif
    """
    if not _is_admin(current_user):
        raise HTTPException(status_code=403, detail="Akses ditolak. Hanya admin yang dapat menghapus pengguna.")

    target = users_db.get(user_id)
    if not target:
        raise HTTPException(status_code=404, detail="Pengguna dengan ID tersebut tidak ditemukan dalam sistem.")

    # Tidak boleh hapus diri sendiri
    if current_user.id == user_id:
        raise HTTPException(status_code=400, detail="Anda tidak dapat menghapus akun Anda sendiri.")

    # Larangan hapus super admin
    if user_id == 1:
        raise HTTPException(status_code=403, detail="Penghapusan ditolak. Pengguna ini adalah Super Admin.")

    # Admin biasa tidak boleh menghapus admin
    if _is_admin(target) and current_user.id != 1:
        raise HTTPException(status_code=403, detail="Penghapusan ditolak. Hanya Super Admin yang dapat menghapus admin.")

    # Tidak boleh hapus user dengan pinjaman aktif
    if _has_active_loans(user_id):
        raise HTTPException(
            status_code=400,
            detail="Pengguna tidak dapat dihapus karena masih memiliki pinjaman aktif. Harap selesaikan pengembalian terlebih dahulu.",
        )

    # Eksekusi hapus
    del users_db[user_id]
    return success_response("Pengguna berhasil dihapus", {"deleted_user_id": user_id})
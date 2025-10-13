# library_management/app/dependencies.py
from fastapi import Header, HTTPException, status
from .data_store import users_db

def get_current_user(x_user_id: int = Header(..., alias="X-User-ID",
                                            description="Identitas pengguna: 1=admin, 101=mahasiswa")):
    user = users_db.get(x_user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pengguna dengan ID tersebut tidak ditemukan dalam sistem."
        )
    return user

def require_admin_role(x_user_id: int = Header(..., alias="X-User-ID")):
    user = users_db.get(x_user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Pengguna dengan ID tersebut tidak ditemukan dalam sistem.")
    if user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Akses ditolak. Hanya admin yang memiliki izin untuk melakukan aksi ini."
        )
    return user

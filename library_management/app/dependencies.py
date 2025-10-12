from fastapi import Header, HTTPException, status
from .data_store import users_db

def get_current_user(x_user_id: int = Header(..., description="Masukkan ID user (misal: 101)")):
    """
    Autentikasi sederhana tanpa JWT.
    Validasi user berdasarkan ID di header.
    """
    user = users_db.get(x_user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User tidak ditemukan."
        )
    return user

def require_admin_role(x_user_id: int = Header(...)):
    user = users_db.get(x_user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User tidak ditemukan.")
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Hanya admin yang dapat mengakses endpoint ini.")
    return user

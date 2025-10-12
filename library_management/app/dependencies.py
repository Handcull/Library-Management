from fastapi import Header, HTTPException, status, Depends
from .data_store import users_db
from .schemas import User

def get_current_user(x_user_id: int = Header(..., description="ID unik pengguna yang melakukan request")) -> User:
    """
    Dependensi untuk mendapatkan data user dari header X-User-ID.
    Ini adalah cara otentikasi sederhana tanpa JWT.
    """
    user = next((u for u in users_db if u.id == x_user_id), None)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID tidak valid atau tidak ditemukan."
        )
    return user

def require_admin_role(current_user: User = Depends(get_current_user)):
    """
    Dependensi yang memastikan bahwa request hanya bisa dilakukan oleh user dengan peran 'admin'.
    Jika peran tidak sesuai, akan menghasilkan error 403 Forbidden.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Akses ditolak. Endpoint ini hanya untuk admin."
        )
    return current_user

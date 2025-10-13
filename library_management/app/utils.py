# library_management/app/utils.py
from typing import Any, Dict

def format_rupiah(nominal: int) -> str:
    # contoh: 5000 -> "Rp 5.000"
    s = f"{nominal:,}".replace(",", ".")
    return f"Rp {s}"

def success_response(message: str, data: Any) -> Dict[str, Any]:
    return {
        "message": message,
        "data": data
    }

# library_management/tests/test_api.py
from fastapi.testclient import TestClient
from library_management.app.main import app
import uuid
from library_management.app.data_store import seed_initial_data
seed_initial_data()  # memastikan database terisi sebelum test berjalan
from datetime import date, timedelta

client = TestClient(app)

ADMIN = {"X-User-ID": "1"}
STEVEN = {"X-User-ID": "101"}
NOHDR = {}  # tanpa header (untuk test error)

def get_data(resp):
    return resp.json().get("data")

def test_books_list_ok():
    r = client.get("/books/")
    assert r.status_code == 200
    body = r.json()
    assert "message" in body and "data" in body
    assert isinstance(body["data"], list)

def test_missing_header_blocked_on_protected_endpoints():
    # /borrow membutuhkan header
    # akan memicu handler global: {"message": "...", "error": "..."}
    # Note: ambil 1 buku dulu
    books = get_data(client.get("/books/"))
    book_id = books[0]["id"]
    r = client.post(f"/borrow/{book_id}", headers=NOHDR)
    assert r.status_code in (400, 422) or r.status_code == 404

def test_borrow_extend_detail_active_history_and_simulate():
    # Ambil buku pertama
    books = get_data(client.get("/books/"))
    assert books, "Seed buku harus ada"
    book_id = books[0]["id"]

    # Pinjam sebagai Steven Jerry
    r_borrow = client.post(f"/borrow/{book_id}", headers=STEVEN)
    assert r_borrow.status_code == 201
    bdata = get_data(r_borrow)
    assert bdata["status"] == "Dipinjam"
    loan_id = bdata["loan_id"]

    # Detail loan
    r_detail = client.get(f"/loans/detail/{loan_id}", headers=STEVEN)
    assert r_detail.status_code == 200
    d = get_data(r_detail)
    assert d["loan_id"] == loan_id
    assert d["status"] == "Dipinjam"
    assert d["denda"].startswith("Rp ")

    # Pinjaman aktif (harus muncul)
    r_active = client.get("/loans/active", headers=STEVEN)
    assert r_active.status_code == 200
    active_list = get_data(r_active)
    assert any(x["loan_id"] == loan_id for x in active_list)

    # Extend sekali (berhasil)
    r_ext = client.post(f"/extend/{loan_id}", headers=STEVEN)
    assert r_ext.status_code == 200
    # Extend kedua (harus gagal 400)
    r_ext2 = client.post(f"/extend/{loan_id}", headers=STEVEN)
    assert r_ext2.status_code == 400

    # Simulasi denda: pakai due_date + 5 hari
    # Ambil due_date dari detail terbaru
    r_detail2 = client.get(f"/loans/detail/{loan_id}", headers=STEVEN)
    due = date.fromisoformat(get_data(r_detail2)["tanggal_jatuh_tempo"])
    planned = due + timedelta(days=5)
    r_sim = client.get(f"/loans/simulate-fine",
                       params={"loan_id": loan_id, "return_date": planned.isoformat()},
                       headers=STEVEN)
    assert r_sim.status_code == 200
    sim = get_data(r_sim)
    assert sim["keterlambatan"].startswith("5 hari")
    assert sim["denda"].startswith("Rp ")

    # History/me harus berisi loan ini
    r_hist_me = client.get("/loans/history/me", headers=STEVEN)
    assert r_hist_me.status_code == 200
    me_list = get_data(r_hist_me)
    assert any(x["loan_id"] == loan_id for x in me_list)

    # History (admin) bisa melihat semua
    r_hist_all = client.get("/loans/history", headers=ADMIN)
    assert r_hist_all.status_code == 200
    all_list = get_data(r_hist_all)
    assert any(x["loan_id"] == loan_id for x in all_list)

    # Kembalikan buku (karena hari ini <= due_date, denda kemungkinan 0)
    r_return = client.post(f"/return/{loan_id}", headers=STEVEN)
    assert r_return.status_code == 200
    ret = get_data(r_return)
    assert ret["loan_id"] == loan_id
    assert ret["denda"].startswith("Rp ")

    # Mengembalikan lagi harus gagal
    r_return_again = client.post(f"/return/{loan_id}", headers=STEVEN)
    assert r_return_again.status_code == 400

def test_history_forbidden_for_student():
    # Mahasiswa tidak boleh akses /loans/history (semua user)
    r = client.get("/loans/history", headers=STEVEN)
    assert r.status_code == 403

def test_admin_can_crud_book():
    # Tambah buku oleh admin
    payload = {"title": "Algoritma", "author": "Knuth", "stock": 3}
    r_create = client.post("/books/", json=payload, headers=ADMIN)
    assert r_create.status_code == 201
    created = get_data(r_create)
    bid = created["id"]

    # Update oleh admin
    r_update = client.put(f"/books/{bid}", json={"stock": 5}, headers=ADMIN)
    assert r_update.status_code == 200
    assert get_data(r_update)["stock"] == 5

    # Hapus oleh admin
    r_del = client.delete(f"/books/{bid}", headers=ADMIN)
    assert r_del.status_code == 200

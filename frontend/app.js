// ================= LOGIN SESSION ===================
const USER_ID = localStorage.getItem("USER_ID") || null;
const USER_ROLE = localStorage.getItem("USER_ROLE") || null;
const USER_NAME = localStorage.getItem("USER_NAME") || null;

// Cek login di setiap halaman kecuali login/register
const protectedPages = ["index.html", "loans.html", "history.html", "simulate.html", "users.html"];
const currentPage = window.location.pathname.split("/").pop();

if (protectedPages.includes(currentPage) && !USER_ID) {
  window.location.href = "login.html"; // redirect kalau belum login
}


// ========== KONFIGURASI BACKEND ==========
const BASE_URL = "http://127.0.0.1:8000";  // Ubah jika beda port


// ========== REQUEST API ==========
async function apiRequest(endpoint, method = "GET", body = null) {
  const headers = {
    "Content-Type": "application/json",
  };

  if (USER_ID) {
    headers["X-User-ID"] = USER_ID;
  }

  const response = await fetch(`${BASE_URL}${endpoint}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : null,
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Terjadi kesalahan API");
  }

  return response.json();
}


// ========== LOAD DAFTAR BUKU DI HALAMAN HOME ==========
async function loadBooks() {
  try {
    const response = await apiRequest("/books");
    const bookList = document.getElementById("bookList");
    bookList.innerHTML = "";

    if (response.data.length === 0) {
      bookList.innerHTML = `<p class="text-muted">Belum ada buku tersedia.</p>`;
      return;
    }

    response.data.forEach(book => {
      const card = document.createElement("div");
      card.className = "col-md-4 mb-3";
      card.innerHTML = `
        <div class="card shadow-sm h-100">
          <div class="card-body">
            <h5 class="card-title">${book.title}</h5>
            <p class="card-text">
              Penulis: ${book.author || "-"}<br>
              Stok: ${book.stock}
            </p>
            <button class="btn btn-success btn-sm" onclick="borrowBook('${book.id}')">
              Pinjam Buku
            </button>
          </div>
        </div>
      `;
      bookList.appendChild(card);
    });

  } catch (error) {
    console.error(error);
    alert("Gagal memuat daftar buku dari server.");
  }
}

// Auto jalan kalau halaman index.html
if (window.location.pathname.endsWith("index.html") || window.location.pathname.endsWith("/")) {
  loadBooks();
}

// ========== PINJAM BUKU ==========
async function borrowBook(bookId) {
  if (!USER_ID) {
    alert("Silakan pilih pengguna terlebih dahulu (Admin atau Mahasiswa).");
    return;
  }

  try {
    const response = await apiRequest(`/borrow/${bookId}`, "POST");
    alert(response.message);
    loadBooks(); // refresh daftar buku setelah dipinjam
  } catch (error) {
    alert("Gagal meminjam buku: " + error.message);
  }
}

// ======================= USER MANAGEMENT ACCESS ==========================
function checkAdminAccess() {
  if (!USER_ID) {
    alert("Silakan login terlebih dahulu!");
    window.location.href = "../login.html";
    return false;
  }
  if (USER_ROLE !== "admin") {
    alert("Akses ditolak! Halaman ini khusus Admin.");
    window.location.href = "../index.html";
    return false;
  }
  return true;
}


// Auto blokir mahasiswa di halaman kelola user
if (window.location.pathname.includes("users.html")) {
  checkAdminAccess();
}

// ================= SHOW ACTIVE USER =================
function showActiveUser() {
  const statusEl = document.getElementById("activeUser");
  if (!statusEl) return;

  if (!USER_ID) {
    statusEl.textContent = "Belum login";
    return;
  }

  statusEl.textContent = `Login sebagai: ${USER_ROLE} (ID: ${USER_ID})`;
}




showActiveUser();

function logout() {
  localStorage.removeItem("USER_ID");
  localStorage.removeItem("USER_NAME");
  window.location.href = "login.html";
}

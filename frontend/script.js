// Определяем базовый URL API (локальный или в Docker)
const API_BASE = window.location.origin.includes("localhost") || window.location.origin.includes("127.0.0.1")
    ? "http://127.0.0.1:8010"
    : "http://backend:8010";

// DOM элементы
const themeToggle = document.getElementById("themeToggle");
const tabs = document.querySelectorAll(".tab-btn");
const contents = document.querySelectorAll(".tab-content");

// Переключение вкладок
tabs.forEach(btn => {
    btn.addEventListener("click", () => {
        const tabId = btn.dataset.tab;
        tabs.forEach(b => b.classList.remove("active"));
        contents.forEach(c => c.classList.remove("active"));
        btn.classList.add("active");
        document.getElementById(`${tabId}-tab`).classList.add("active");
        // Перезагружаем данные для активной вкладки
        if (tabId === "products") loadProducts();
        if (tabId === "suppliers") loadSuppliers();
        if (tabId === "special") { loadStock(); loadLowStock(); }
        if (tabId === "supplies") { loadSuppliersForSelect(); loadProductsForSelect(); loadSupplyHistory(); }
    });
});

// Тема
themeToggle.addEventListener("click", () => {
    const isDark = document.documentElement.getAttribute("data-theme") === "dark";
    document.documentElement.setAttribute("data-theme", isDark ? "light" : "dark");
    themeToggle.textContent = isDark ? "🌙 Тёмная тема" : "☀️ Светлая тема";
});

// ========== Товары ==========
const productsList = document.getElementById("productsList");
async function loadProducts() {
    const res = await fetch(`${API_BASE}/api/products`);
    const products = await res.json();
    renderProducts(products);
}

function renderProducts(products) {
    productsList.innerHTML = "";
    products.forEach(p => {
        const card = document.createElement("div");
        card.className = "card";
        card.innerHTML = `
            <h3>${p.name}</h3>
            <p>Количество: ${p.quantity}</p>
            <p>Цена: ${p.price} руб.</p>
            <p>Мин. остаток: ${p.min_quantity}</p>
            <button class="delete-product" data-id="${p.id}">🗑 Удалить</button>
            <button class="edit-product" data-id="${p.id}">✏️ Редактировать</button>
        `;
        productsList.appendChild(card);
    });
    document.querySelectorAll(".delete-product").forEach(btn => {
        btn.addEventListener("click", async (e) => {
            const id = btn.dataset.id;
            await fetch(`${API_BASE}/api/products/${id}`, { method: "DELETE" });
            loadProducts();
        });
    });
    // Редактирование (упрощённо – можно сделать модальное окно, здесь для краткости prompt)
    document.querySelectorAll(".edit-product").forEach(btn => {
        btn.addEventListener("click", async (e) => {
            const id = btn.dataset.id;
            const newName = prompt("Новое название");
            const newQty = prompt("Новое количество");
            const newPrice = prompt("Новая цена");
            const newMin = prompt("Новый мин. остаток");
            if (newName && newQty && newPrice && newMin) {
                await fetch(`${API_BASE}/api/products/${id}`, {
                    method: "PUT",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ name: newName, quantity: +newQty, price: +newPrice, min_quantity: +newMin })
                });
                loadProducts();
            }
        });
    });
}

document.getElementById("productForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    const name = document.getElementById("prodName").value;
    const quantity = parseInt(document.getElementById("prodQuantity").value);
    const price = parseFloat(document.getElementById("prodPrice").value);
    const min_quantity = parseInt(document.getElementById("prodMin").value);
    await fetch(`${API_BASE}/api/products`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, quantity, price, min_quantity })
    });
    e.target.reset();
    loadProducts();
});

// ========== Поставщики ==========
const suppliersList = document.getElementById("suppliersList");
async function loadSuppliers() {
    const res = await fetch(`${API_BASE}/api/suppliers`);
    const suppliers = await res.json();
    renderSuppliers(suppliers);
}

function renderSuppliers(suppliers) {
    suppliersList.innerHTML = "";
    suppliers.forEach(s => {
        const card = document.createElement("div");
        card.className = "card";
        card.innerHTML = `
            <h3>${s.name}</h3>
            <p>Контакт: ${s.contact || "—"}</p>
            <button class="delete-supplier" data-id="${s.id}">🗑 Удалить</button>
        `;
        suppliersList.appendChild(card);
    });
    document.querySelectorAll(".delete-supplier").forEach(btn => {
        btn.addEventListener("click", async (e) => {
            const id = btn.dataset.id;
            await fetch(`${API_BASE}/api/suppliers/${id}`, { method: "DELETE" });
            loadSuppliers();
        });
    });
}

document.getElementById("supplierForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    const name = document.getElementById("supName").value;
    const contact = document.getElementById("supContact").value;
    await fetch(`${API_BASE}/api/suppliers`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, contact })
    });
    e.target.reset();
    loadSuppliers();
});

// ========== Поставки ==========
async function loadProductsForSelect() {
    const res = await fetch(`${API_BASE}/api/products`);
    const products = await res.json();
    const select = document.getElementById("supplyProductId");
    select.innerHTML = '<option value="">Выберите товар</option>';
    products.forEach(p => {
        const opt = document.createElement("option");
        opt.value = p.id;
        opt.textContent = `${p.name} (остаток: ${p.quantity})`;
        select.appendChild(opt);
    });
}
async function loadSuppliersForSelect() {
    const res = await fetch(`${API_BASE}/api/suppliers`);
    const suppliers = await res.json();
    const select = document.getElementById("supplySupplierId");
    select.innerHTML = '<option value="">Выберите поставщика</option>';
    suppliers.forEach(s => {
        const opt = document.createElement("option");
        opt.value = s.id;
        opt.textContent = s.name;
        select.appendChild(opt);
    });
}

document.getElementById("supplyForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    const product_id = document.getElementById("supplyProductId").value;
    const supplier_id = document.getElementById("supplySupplierId").value;
    const quantity = parseInt(document.getElementById("supplyQuantity").value);
    const price_per_unit = parseFloat(document.getElementById("supplyPrice").value);
    if (!product_id || !supplier_id) return alert("Выберите товар и поставщика");
    await fetch(`${API_BASE}/api/supplies`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ product_id, supplier_id, quantity, price_per_unit })
    });
    e.target.reset();
    loadProductsForSelect();  // обновим select товаров
    loadSupplyHistory();
    if (document.querySelector(".tab-btn.active").dataset.tab === "products") loadProducts();
});

async function loadSupplyHistory() {
    const res = await fetch(`${API_BASE}/api/supplies/history`);
    const history = await res.json();
    const container = document.getElementById("suppliesHistory");
    container.innerHTML = "";
    history.forEach(h => {
        const item = document.createElement("div");
        item.className = "timeline-item";
        item.innerHTML = `
            <strong>${h.product_name}</strong> от ${h.supplier_name}<br>
            Кол-во: ${h.quantity}, цена за ед.: ${h.price_per_unit} руб.<br>
            Дата: ${new Date(h.supply_date).toLocaleString()}
        `;
        container.appendChild(item);
    });
}

// ========== Специальные отчёты ==========
async function loadStock() {
    const res = await fetch(`${API_BASE}/api/stock`);
    const stock = await res.json();
    const container = document.getElementById("stockList");
    container.innerHTML = "";
    stock.forEach(p => {
        const card = document.createElement("div");
        card.className = "card";
        card.innerHTML = `<h3>${p.name}</h3><p>Остаток: ${p.quantity} шт.</p><p>Цена: ${p.price} руб.</p>`;
        container.appendChild(card);
    });
}
async function loadLowStock() {
    const res = await fetch(`${API_BASE}/api/low-stock`);
    const low = await res.json();
    const container = document.getElementById("lowStockList");
    container.innerHTML = "";
    if (low.length === 0) {
        container.innerHTML = "<p>✅ Все товары в достаточном количестве</p>";
        return;
    }
    low.forEach(p => {
        const card = document.createElement("div");
        card.className = "card";
        card.innerHTML = `<h3>${p.name}</h3><p>Остаток: ${p.quantity} (мин. ${p.min_quantity})</p><span style="color:red;">⚠️ Требуется закупка!</span>`;
        container.appendChild(card);
    });
}

// Инициализация первой вкладки и загрузка данных
loadProducts();
loadSuppliers();
loadSupplyHistory();
loadProductsForSelect();
loadSuppliersForSelect();
// ============================================================
// НАСТРОЙКИ
// ============================================================
const API_URL = '/api';
let currentUser = null;
let currentCategory = '';
let cartItems = [];
let isCartOpen = false;
let statusCheckInterval = null;
let currentOrderId = null;
let allOrders = [];

// ============================================================
// ОЧИСТКА ВСЕХ СТАРЫХ ТОКЕНОВ
// ============================================================
function clearAllTokens() {
    const keys = Object.keys(localStorage);
    keys.forEach(key => {
        if (key.startsWith('access_token_')) {
            localStorage.removeItem(key);
        }
    });
    console.log('🗑️ Все старые токены очищены');
}

// ============================================================
// JWT ФУНКЦИИ
// ============================================================
function getTokenKey() {
    const userId = localStorage.getItem('current_user_id') || 'default';
    return `access_token_${userId}`;
}

function getToken() {
    const token = localStorage.getItem(getTokenKey());
    console.log('🔑 Получаю токен для пользователя:', localStorage.getItem('current_user_id'));
    console.log('📝 Токен:', token ? token.substring(0, 20) + '...' : '❌ нет');
    return token;
}

function setToken(token) {
    console.log('💾 Сохраняю токен для пользователя:', localStorage.getItem('current_user_id'));
    console.log('📝 Токен:', token ? token.substring(0, 20) + '...' : '❌ нет');
    localStorage.setItem(getTokenKey(), token);
}

function clearToken() {
    console.log('🗑️ Очищаю токен для пользователя:', localStorage.getItem('current_user_id'));
    localStorage.removeItem(getTokenKey());
}

function getAuthHeaders() {
    const token = getToken();
    return {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
    };
}

function isAuthenticated() {
    const hasToken = getToken() !== null;
    const hasUser = currentUser !== null;
    console.log('🔐 Проверка авторизации: hasToken=' + hasToken + ', hasUser=' + hasUser);
    return hasToken && hasUser;
}

// ============================================================
// ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
// ============================================================
function isMaxApp() {
    return typeof window.WebApp !== 'undefined' && window.WebApp.initDataUnsafe;
}

function closeApp() {
    if (statusCheckInterval) {
        clearInterval(statusCheckInterval);
        statusCheckInterval = null;
    }
    if (isMaxApp() && window.WebApp) {
        window.WebApp.close();
    }
}

function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = 'toast ' + type + ' show';
    clearTimeout(toast._timeout);
    toast._timeout = setTimeout(() => toast.classList.remove('show'), 3000);
}

// ============================================================
// ОТКРЫТИЕ/ЗАКРЫТИЕ
// ============================================================
function toggleCart() {
    isCartOpen = !isCartOpen;
    document.getElementById('cartModal').classList.toggle('visible', isCartOpen);
    document.getElementById('cartOverlay').classList.toggle('visible', isCartOpen);
}

function openOrderForm() {
    if (cartItems.length === 0) {
        showToast('Корзина пуста', 'error');
        return;
    }
    document.getElementById('orderModal').classList.add('visible');
    document.getElementById('orderAddressInput').value = '';
    document.getElementById('orderPhoneInput').value = '';
    document.getElementById('addressSuggestions').style.display = 'none';
    setTimeout(() => document.getElementById('orderAddressInput').focus(), 100);
}

function closeOrderForm() {
    document.getElementById('orderModal').classList.remove('visible');
    document.getElementById('addressSuggestions').style.display = 'none';
}

function showHistory() {
    const overlay = document.getElementById('historyOverlay');
    const list = document.getElementById('historyList');
    const historyOrders = allOrders.filter(o => o.status === 'completed' || o.status === 'cancelled');

    if (historyOrders.length === 0) {
        list.innerHTML = `
            <div class="empty-state">
                <span class="icon">📭</span>
                <p>История заказов пуста</p>
            </div>
        `;
    } else {
        let html = '';
        const statusMap = { 'completed': '✅ Выполнен', 'cancelled': '❌ Отменён' };
        historyOrders.forEach(order => {
            const statusClass = order.status === 'completed' ? 'completed' : 'cancelled';
            html += `
                <div class="history-item">
                    <div class="top-row">
                        <span style="font-weight:600;">Заказ #${order.id}</span>
                        <span class="status-badge ${statusClass}">${statusMap[order.status] || order.status}</span>
                    </div>
                    <div class="details">
                        <div class="row"><span>💰</span><span>${order.total} ₽</span></div>
                        <div class="row"><span>📍</span><span>${order.address || '-'}</span></div>
                        <div class="row"><span>🕐</span><span>${new Date(order.created_at).toLocaleString('ru-RU')}</span></div>
                    </div>
                    ${order.items && order.items.length > 0 ? `
                        <div style="margin-top:6px;padding-top:6px;border-top:1px solid #f1f3f5;font-size:13px;color:#495057;">
                            ${order.items.map(item => `
                                <div style="display:flex;justify-content:space-between;padding:2px 0;">
                                    <span>${item.product_name || item.product}</span>
                                    <span>×${item.quantity} = ${item.total || item.price * item.quantity} ₽</span>
                                </div>
                            `).join('')}
                        </div>
                    ` : ''}
                </div>
            `;
        });
        list.innerHTML = html;
    }
    overlay.classList.add('visible');
}

function closeHistory(e) {
    if (e && e.target !== e.currentTarget) return;
    document.getElementById('historyOverlay').classList.remove('visible');
}

// ============================================================
// АВТОРИЗАЦИЯ
// ============================================================
async function authUser(userId, username, firstName) {
    try {
        clearToken();
        currentUser = null;
        localStorage.setItem('current_user_id', String(userId));

        const response = await fetch(`${API_URL}/auth/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                user_id: userId,
                username: username || `user_${userId}`,
                first_name: firstName || 'Пользователь'
            })
        });
        const data = await response.json();
        if (data.success) {
            currentUser = data.user;
            setToken(data.access);
            document.getElementById('userDisplay').textContent = '👋 ' + currentUser.first_name;
            return true;
        }
        return false;
    } catch (e) {
        console.error('Auth error:', e);
        return false;
    }
}

async function reAuth() {
    if (isMaxApp()) {
        const user = window.WebApp.initDataUnsafe?.user;
        if (user) {
            return await authUser(
                user.id,
                user.username || `max_${user.id}`,
                user.first_name || 'Пользователь'
            );
        }
    }
    return false;
}

const testUsers = {
    1: { username: 'ivan', name: 'Иван' },
    2: { username: 'maria', name: 'Мария' },
    3: { username: 'petr', name: 'Петр' }
};

// ============================================================
// УНИВЕРСАЛЬНЫЙ FETCH
// ============================================================
async function apiFetch(url, options = {}) {
    let response = await fetch(url, options);
    
    if (response.status === 401) {
        console.log('🔄 401 Unauthorized, переавторизация...');
        const reAuthSuccess = await reAuth();
        if (reAuthSuccess) {
            options.headers = getAuthHeaders();
            response = await fetch(url, options);
        }
    }
    
    return response;
}

// ============================================================
// КАТЕГОРИИ
// ============================================================
async function loadCategories() {
    try {
        const response = await fetch(`${API_URL}/categories/`);
        const categories = await response.json();
        const container = document.getElementById('categories');
        container.innerHTML = '<button class="category-btn active" data-slug="">🏠 Все</button>';
        categories.forEach(cat => {
            if (!cat.slug) return;
            const btn = document.createElement('button');
            btn.className = 'category-btn';
            btn.dataset.slug = cat.slug;
            btn.textContent = cat.name;
            btn.onclick = () => {
                currentCategory = cat.slug;
                document.querySelectorAll('.category-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                loadProducts(cat.slug);
            };
            container.appendChild(btn);
        });
    } catch (e) { console.error('Error loading categories:', e); }
}

// ============================================================
// ТОВАРЫ
// ============================================================
async function loadProducts(category = '') {
    try {
        const url = category ? `${API_URL}/products/?category=${category}` : `${API_URL}/products/`;
        const response = await fetch(url);
        const products = await response.json();
        const container = document.getElementById('products');

        if (!products || products.length === 0) {
            container.innerHTML = '<div class="empty-state"><span class="icon">📦</span>Товаров пока нет</div>';
            return;
        }

        container.innerHTML = '';
        products.forEach(product => {
            const inStock = product.stock > 0;
            const card = document.createElement('div');
            card.className = 'product-card';

            let imageHtml = '';
            if (product.image) {
                imageHtml = `<img src="${product.image}" alt="${product.name}" onerror="this.parentElement.innerHTML='<div class=\\'no-image\\'>📷</div>'">`;
            } else {
                imageHtml = `<div class="no-image">📷</div>`;
            }

            card.innerHTML = `
                ${imageHtml}
                <h3>${product.name}</h3>
                <div class="price">${product.price} ₽</div>
                <div class="stock ${inStock ? 'in-stock' : 'out-of-stock'}">${inStock ? '✅ ' + product.stock + ' шт' : '❌ Нет'}</div>
                <button ${!inStock ? 'disabled' : ''} onclick="addToCart(${product.id}, this)">
                    ${inStock ? '🛒 В корзину' : 'Нет в наличии'}
                </button>
            `;
            container.appendChild(card);
        });
    } catch (e) {
        console.error('Error loading products:', e);
        document.getElementById('products').innerHTML = '<div class="empty-state"><span class="icon">❌</span>Ошибка загрузки</div>';
    }
}

// ============================================================
// КОРЗИНА
// ============================================================
async function addToCart(productId, button) {
    if (!isAuthenticated()) {
        showToast('Пожалуйста, авторизуйтесь', 'error');
        return;
    }

    if (button) {
        button.disabled = true;
        button.textContent = '⏳...';
    }

    try {
        const response = await apiFetch(`${API_URL}/cart/add/`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({ product_id: productId, quantity: 1 })
        });
        
        if (response.ok) {
            showToast('✅ Товар добавлен', 'success');
            await loadCart();
        } else {
            const data = await response.json();
            showToast('❌ ' + (data.error || 'Ошибка'), 'error');
        }
    } catch (e) {
        console.error('Error adding to cart:', e);
        showToast('❌ Ошибка', 'error');
    } finally {
        if (button) {
            button.disabled = false;
            button.textContent = '🛒 В корзину';
        }
    }
}

async function removeFromCart(itemId) {
    try {
        const response = await apiFetch(`${API_URL}/cart/remove/`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({ item_id: itemId })
        });
        if (response.ok) {
            await loadCart();
        }
    } catch (e) { console.error('Error removing from cart:', e); }
}

async function updateQuantity(itemId, change) {
    try {
        const response = await apiFetch(`${API_URL}/cart/update_quantity/`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({ item_id: itemId, quantity: change })
        });
        if (response.ok) {
            await loadCart();
        }
    } catch (e) { console.error('Error updating quantity:', e); }
}

async function loadCart() {
    if (!isAuthenticated()) {
        document.getElementById('cartItems').innerHTML = '<div class="cart-empty"><span class="icon">🛒</span>Корзина пуста</div>';
        document.getElementById('cartTotal').textContent = '0 ₽';
        document.getElementById('cartCount').textContent = '0';
        document.getElementById('orderBtn').disabled = true;
        document.getElementById('cartBadge').classList.add('hidden');
        cartItems = [];
        return;
    }

    try {
        const response = await apiFetch(`${API_URL}/cart/`, {
            headers: getAuthHeaders()
        });
        const cart = await response.json();
        const container = document.getElementById('cartItems');
        const totalEl = document.getElementById('cartTotal');
        const countEl = document.getElementById('cartCount');
        const orderBtn = document.getElementById('orderBtn');
        const badge = document.getElementById('cartBadge');

        if (!cart.items || cart.items.length === 0) {
            container.innerHTML = '<div class="cart-empty"><span class="icon">🛒</span>Корзина пуста</div>';
            totalEl.textContent = '0 ₽';
            countEl.textContent = '0';
            orderBtn.disabled = true;
            badge.classList.add('hidden');
            cartItems = [];
            return;
        }

        countEl.textContent = cart.items.length;
        badge.textContent = cart.items.length;
        badge.classList.remove('hidden');
        orderBtn.disabled = false;
        let total = 0;
        container.innerHTML = '';

        cart.items.forEach(item => {
            const itemTotal = item.total || (item.product.price * item.quantity);
            total += itemTotal;
            cartItems.push(item);

            const div = document.createElement('div');
            div.className = 'cart-item';
            div.innerHTML = `
                <span class="name">${item.product.name}</span>
                <div class="controls">
                    <button class="qty-btn" onclick="updateQuantity(${item.id}, -1)">−</button>
                    <span class="qty">${item.quantity}</span>
                    <button class="qty-btn" onclick="updateQuantity(${item.id}, 1)">+</button>
                    <span class="item-price">${itemTotal} ₽</span>
                    <button class="remove-btn" onclick="removeFromCart(${item.id})">✕</button>
                </div>
            `;
            container.appendChild(div);
        });

        totalEl.textContent = total + ' ₽';
    } catch (e) { console.error('Error loading cart:', e); }
}

// ============================================================
// ЗАКАЗ
// ============================================================
async function submitOrder() {
    if (!isAuthenticated()) {
        showToast('Пожалуйста, авторизуйтесь', 'error');
        return;
    }

    const address = document.getElementById('orderAddressInput').value.trim();
    const phone = document.getElementById('orderPhoneInput').value.trim();

    if (!address) {
        showToast('Введите адрес доставки', 'error');
        document.getElementById('orderAddressInput').focus();
        return;
    }

    if (!phone || phone.length < 5) {
        showToast('Введите номер телефона', 'error');
        document.getElementById('orderPhoneInput').focus();
        return;
    }

    // Проверяем телефон
    const cleanPhone = phone.replace(/[^0-9]/g, '');
    if (cleanPhone.length !== 11 || !cleanPhone.startsWith('7')) {
        showToast('Введите корректный номер телефона (+7 999 999-99-99)', 'error');
        document.getElementById('orderPhoneInput').focus();
        return;
    }

    const orderBtn = document.getElementById('orderBtn');
    orderBtn.disabled = true;
    orderBtn.textContent = '⏳...';

    try {
        const response = await apiFetch(`${API_URL}/orders/`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({
                address: address,
                phone: phone,
                comment: ''
            })
        });

        if (response.ok) {
            const data = await response.json();
            showToast('✅ Заказ оформлен!', 'success');
            cartItems = [];
            await loadCart();
            await loadProducts(currentCategory);
            closeOrderForm();
            toggleCart();
            await checkOrderStatus();

            if (isMaxApp()) {
                setTimeout(() => {
                    if (confirm('Заказ оформлен! Закрыть приложение?')) {
                        closeApp();
                    }
                }, 1500);
            }
        } else {
            const data = await response.json();
            showToast('❌ ' + (data.error || 'Ошибка'), 'error');
        }
    } catch (e) {
        console.error('Error creating order:', e);
        showToast('❌ Ошибка при оформлении', 'error');
    } finally {
        orderBtn.disabled = false;
        orderBtn.textContent = 'Оформить заказ';
    }
}

// ============================================================
// АДРЕС: АВТОДОПОЛНЕНИЕ
// ============================================================
const cities = [
    'Москва', 'Санкт-Петербург', 'Новосибирск', 'Екатеринбург', 'Казань',
    'Нижний Новгород', 'Челябинск', 'Самара', 'Омск', 'Ростов-на-Дону',
    'Уфа', 'Красноярск', 'Воронеж', 'Пермь', 'Волгоград',
    'Краснодар', 'Саратов', 'Тюмень', 'Тольятти', 'Ижевск',
    'Барнаул', 'Ульяновск', 'Иркутск', 'Хабаровск', 'Ярославль',
    'Владивосток', 'Махачкала', 'Томск', 'Оренбург', 'Кемерово',
    'Новокузнецк', 'Рязань', 'Набережные Челны', 'Пенза', 'Липецк',
    'Киров', 'Чебоксары', 'Калининград', 'Брянск', 'Курск',
    'Иваново', 'Магнитогорск', 'Тверь', 'Ставрополь', 'Сочи',
    'Белгород', 'Архангельск', 'Владимир', 'Смоленск', 'Чита'
];

function getAddressSuggestions(query) {
    if (!query || query.length < 2) return [];
    const lowerQuery = query.toLowerCase();
    const results = [];
    for (const city of cities) {
        if (city.toLowerCase().includes(lowerQuery)) {
            results.push(city);
        }
    }
    return results.slice(0, 8);
}

function showAddressSuggestions(query) {
    const container = document.getElementById('addressSuggestions');
    if (!container) return;
    
    if (query.length < 2) {
        container.style.display = 'none';
        return;
    }
    
    const results = getAddressSuggestions(query);
    if (results.length === 0) {
        container.style.display = 'none';
        return;
    }
    
    container.innerHTML = '';
    results.forEach(item => {
        const div = document.createElement('div');
        div.className = 'suggestion-item';
        div.textContent = item;
        div.onmousedown = function() {
            document.getElementById('orderAddressInput').value = item;
            container.style.display = 'none';
        };
        container.appendChild(div);
    });
    container.style.display = 'block';
}

// ============================================================
// ТЕЛЕФОН: МАСКА И ВАЛИДАЦИЯ
// ============================================================
function setPhoneMask() {
    const phoneInput = document.getElementById('orderPhoneInput');
    if (!phoneInput) return;
    
    phoneInput.addEventListener('input', function(e) {
        let value = this.value.replace(/[^0-9]/g, '');
        if (value.startsWith('7')) value = value.substring(1);
        else if (value.startsWith('8')) value = value.substring(1);
        if (value.length > 10) value = value.substring(0, 10);
        
        let formatted = '+7';
        if (value.length > 0) formatted += ' (' + value.substring(0, 3);
        if (value.length >= 4) formatted += ') ' + value.substring(3, 6);
        if (value.length >= 7) formatted += '-' + value.substring(6, 8);
        if (value.length >= 9) formatted += '-' + value.substring(8, 10);
        this.value = formatted;
        
        const errorEl = document.getElementById('phoneError');
        const submitBtn = document.getElementById('submitOrderBtn');
        const clean = this.value.replace(/[^0-9]/g, '');
        if (clean.length === 11 && clean.startsWith('7')) {
            errorEl.style.display = 'none';
            submitBtn.disabled = false;
        } else if (this.value.length > 3) {
            errorEl.style.display = 'block';
            submitBtn.disabled = true;
        } else {
            errorEl.style.display = 'none';
            submitBtn.disabled = false;
        }
    });
}

// ============================================================
// СТАТУС ЗАКАЗА
// ============================================================
function displayOrder(order) {
    const bar = document.getElementById('orderStatusBar');
    const badge = document.getElementById('orderStatusBadge');
    const idEl = document.getElementById('orderId');
    const totalEl = document.getElementById('orderTotal');
    const addressEl = document.getElementById('orderAddress');
    const phoneEl = document.getElementById('orderPhone');
    const dateEl = document.getElementById('orderDate');
    const itemsEl = document.getElementById('orderItems');

    if (!order || order.status === 'completed' || order.status === 'cancelled') {
        bar.classList.remove('visible');
        currentOrderId = null;
        return;
    }

    currentOrderId = order.id;
    bar.classList.add('visible');

    const statusMap = {
        'new': '🆕 Новый',
        'processing': '🔄 В обработке',
        'shipped': '🚚 В доставке',
        'completed': '✅ Выполнен',
        'cancelled': '❌ Отменён'
    };

    badge.textContent = statusMap[order.status] || order.status;
    badge.className = 'status-badge ' + order.status;
    idEl.textContent = '#' + order.id;
    totalEl.textContent = order.total + ' ₽';
    addressEl.textContent = order.address || '-';
    phoneEl.textContent = order.phone || '-';
    dateEl.textContent = order.created_at ? new Date(order.created_at).toLocaleString('ru-RU') : '-';

    if (order.items && order.items.length > 0) {
        itemsEl.innerHTML = order.items.map(item => `
            <div class="item">
                <span>${item.product_name || item.product}</span>
                <span>×${item.quantity} = ${item.total || item.price * item.quantity} ₽</span>
            </div>
        `).join('');
    } else {
        itemsEl.innerHTML = '';
    }
}

async function checkOrderStatus() {
    if (!isAuthenticated()) return;

    try {
        const response = await apiFetch(`${API_URL}/orders/`, {
            headers: getAuthHeaders()
        });
        if (!response.ok) return;

        const orders = await response.json();
        allOrders = orders;

        const historyCount = orders.filter(o => o.status === 'completed' || o.status === 'cancelled').length;
        const badge = document.getElementById('historyBadge');
        if (historyCount > 0) {
            badge.textContent = historyCount;
            badge.classList.remove('hidden');
        } else {
            badge.classList.add('hidden');
        }

        if (!orders || orders.length === 0) {
            displayOrder(null);
            return;
        }

        const activeOrder = orders.find(o => o.status !== 'completed' && o.status !== 'cancelled');
        displayOrder(activeOrder || null);

    } catch (e) {
        console.error('Error checking order status:', e);
    }
}

function manualCheck() {
    checkOrderStatus();
    showToast('🔄 Проверка статуса...', 'info');
}

// ============================================================
// ПЕРЕКЛЮЧЕНИЕ ПОЛЬЗОВАТЕЛЕЙ
// ============================================================
async function switchUser(userId) {
    const user = testUsers[userId];
    if (!user) return;
    const success = await authUser(userId, user.username, user.name);
    if (success) {
        document.querySelectorAll('#userButtons button').forEach(btn => {
            btn.classList.toggle('active', parseInt(btn.dataset.user) === userId);
        });
        currentOrderId = null;
        await loadCart();
        await checkOrderStatus();
        showToast('👋 Привет, ' + user.name + '!', 'success');
    }
}

// ============================================================
// ИНИЦИАЛИЗАЦИЯ
// ============================================================
async function init() {
    clearAllTokens();
    
    // Инициализация маски телефона
    setPhoneMask();
    
    // Обработка адресных подсказок
    const addressInput = document.getElementById('orderAddressInput');
    if (addressInput) {
        addressInput.addEventListener('input', function() {
            showAddressSuggestions(this.value);
        });
        addressInput.addEventListener('blur', function() {
            setTimeout(() => {
                document.getElementById('addressSuggestions').style.display = 'none';
            }, 200);
        });
        addressInput.addEventListener('focus', function() {
            if (this.value.length >= 2) {
                showAddressSuggestions(this.value);
            }
        });
    }
    
    if (isMaxApp()) {
        const user = window.WebApp.initDataUnsafe?.user;
        if (user) {
            await authUser(
                user.id,
                user.username || `max_${user.id}`,
                user.first_name || 'Пользователь'
            );
        }
    } else {
        document.getElementById('devPanel').style.display = 'block';
        const savedUserId = localStorage.getItem('test_user_id') || 1;
        const user = testUsers[savedUserId] || testUsers[1];
        await authUser(parseInt(savedUserId), user.username, user.name);

        document.querySelectorAll('#userButtons button').forEach(btn => {
            btn.classList.toggle('active', parseInt(btn.dataset.user) === parseInt(savedUserId));
            btn.onclick = () => {
                const userId = parseInt(btn.dataset.user);
                localStorage.setItem('test_user_id', userId);
                switchUser(userId);
            };
        });
    }

    await loadCategories();
    await loadProducts();
    await loadCart();
    await checkOrderStatus();

    if (statusCheckInterval) {
        clearInterval(statusCheckInterval);
    }
    statusCheckInterval = setInterval(checkOrderStatus, 10000);
}

document.addEventListener('DOMContentLoaded', init);
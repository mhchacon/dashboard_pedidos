const loginForm = document.getElementById('login-form');
const loginError = document.getElementById('login-error');
const logoutMessage = document.getElementById('logout-message');
const API_URL = "";

loginForm.onsubmit = async (e) => {
    e.preventDefault();
    loginError.textContent = '';
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const res = await fetch(`${API_URL}/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
    });
    const data = await res.json();
    if (data.success) {
        localStorage.setItem('role', data.role);
        window.location.href = 'dashboard.html';
    } else {
        loginError.textContent = data.message || 'Erro no login';
    }
}; 
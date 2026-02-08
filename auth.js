// Переключение вкладок Вход/Регистрация
function switchTab(tabName) {
    document.querySelectorAll('.auth-form').forEach(form => {
        form.classList.remove('active');
    });
    document.querySelectorAll('.tab').forEach(tab => {
        tab.classList.remove('active');
    });
    
    document.getElementById(tabName + 'Form').classList.add('active');
    document.querySelector(`.tab[onclick*="${tabName}"]`).classList.add('active');
}

// Обработка форм
document.addEventListener('DOMContentLoaded', function() {
    // Форма входа
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            e.preventDefault();
            // ЗАГЛУШКА - потом замените на fetch
            const username = this.querySelector('input[type="text"]').value;
            console.log('Вход для пользователя:', username);
            
            // Переход в личный кабинет
            window.location.href = 'dashboard.html';
        });
    }
    
    // Форма регистрации
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', function(e) {
            e.preventDefault();
            // ЗАГЛУШКА
            console.log('Регистрация:', {
                username: this.querySelector('input[type="text"]').value,
                password: this.querySelector('input[type="password"]').value,
                role: this.querySelector('select').value
            });
            
            alert('Аккаунт создан! Теперь войдите.');
            switchTab('login');
        });
    }
});
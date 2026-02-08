// ЗАГЛУШКИ API (потом замените на fetch)
const API = {
    posts: {
        create: (data) => Promise.resolve({ 
            id: Date.now(), 
            ...data, 
            author: 'Вы', 
            date: new Date().toLocaleDateString('ru-RU'),
            status: 'draft'
        }),
        list: () => Promise.resolve([]),
        update: (id, data) => Promise.resolve({ id, ...data }),
        delete: (id) => Promise.resolve(),
        publish: (id) => Promise.resolve()
    }
};

// Создание поста
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('createPostForm');
    if (form) {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const postData = {
                title: document.getElementById('postTitle').value,
                content: document.getElementById('postContent').value
            };
            
            try {
                await API.posts.create(postData);
                loadPosts(); // Обновляем список
                this.reset(); // Очищаем форму
                alert('Пост создан!');
            } catch {
                alert('Ошибка создания поста');
            }
        });
    }
    
    loadPosts();
});

// Загрузка постов
async function loadPosts() {
    const posts = await API.posts.list();
    renderPosts(posts);
}

// Отображение постов
function renderPosts(posts) {
    const container = document.getElementById('postsList');
    if (!posts || posts.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: #666; padding: 40px;">Постов пока нет. Создайте первый!</p>';
        return;
    }
    
    container.innerHTML = posts.map(post => `
        <div class="post">
            <div class="post-header">
                <div>
                    <h3 class="post-title">${post.title}</h3>
                    <div class="post-meta">
                        <span>${post.date}</span>
                        <span>${post.author}</span>
                        <span class="post-status ${post.status === 'published' ? 'status-published' : 'status-draft'}">
                            ${post.status === 'published' ? '📢 Опубликован' : '📝 Черновик'}
                        </span>
                    </div>
                </div>
            </div>
            <p>${post.content}</p>
            <div class="post-actions">
                <button onclick="editPost('${post.id}')">✏️ Редактировать</button>
                <button onclick="deletePost('${post.id}')">🗑️ Удалить</button>
                ${post.status !== 'published' ? 
                    `<button onclick="publishPost('${post.id}')" style="background: #006633; color: white;">📢 Опубликовать</button>` : ''}
            </div>
        </div>
    `).join('');
}

// Функции для кнопок
window.editPost = function(id) {
    document.getElementById('editModal').style.display = 'flex';
};

window.deletePost = function(id) {
    if (confirm('Удалить этот пост?')) {
        API.posts.delete(id);
        loadPosts();
    }
};

window.publishPost = function(id) {
    API.posts.publish(id);
    alert('Пост опубликован!');
    loadPosts();
};

window.logout = function() {
    if (confirm('Выйти из системы?')) {
        window.location.href = 'index.html';
    }
};

window.closeModal = function() {
    document.getElementById('editModal').style.display = 'none';
};
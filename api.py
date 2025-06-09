import uvicorn
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import secrets
from datetime import datetime, timedelta
from database import DatabaseManager
from config import API_HOST, API_PORT, ADMIN_USERNAME, ADMIN_PASSWORD


app = FastAPI(
    title="Blog Admin API",
    description="API для управления постами блога",
    version="1.0.0"
)

security = HTTPBasic()
db = DatabaseManager()


class PostCreate(BaseModel):
    title: str
    content: str

class PostUpdate(BaseModel):
    title: str
    content: str

class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    created_at: str

class HealthResponse(BaseModel):
    status: str
    message: str


def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, ADMIN_USERNAME)
    correct_password = secrets.compare_digest(credentials.password, ADMIN_PASSWORD)

    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=401,
            detail="Неверные учетные данные",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


admin_html = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Админ-панель блога</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }

        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }

        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }

        .content {
            padding: 30px;
        }

        .section {
            margin-bottom: 40px;
            padding: 25px;
            border-radius: 15px;
            background: #f8f9fa;
            border-left: 5px solid #667eea;
        }

        .section h2 {
            color: #333;
            margin-bottom: 20px;
            font-size: 1.5em;
        }

        .form-group {
            margin-bottom: 20px;
        }

        label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #555;
        }

        input, textarea {
            width: 100%;
            padding: 12px 15px;
            border: 2px solid #e9ecef;
            border-radius: 10px;
            font-size: 16px;
            transition: border-color 0.3s ease;
        }

        input:focus, textarea:focus {
            outline: none;
            border-color: #667eea;
        }

        textarea {
            min-height: 120px;
            resize: vertical;
        }

        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 25px;
            border-radius: 10px;
            cursor: pointer;
            font-size: 16px;
            font-weight: 600;
            transition: transform 0.2s ease;
            margin-right: 10px;
        }

        .btn:hover {
            transform: translateY(-2px);
        }

        .btn-danger {
            background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%);
        }

        .posts-grid {
            display: grid;
            gap: 20px;
            margin-top: 20px;
        }

        .post-card {
            background: white;
            border-radius: 15px;
            padding: 20px;
            border: 2px solid #e9ecef;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }

        .post-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        }

        .post-title {
            font-size: 1.2em;
            font-weight: bold;
            color: #333;
            margin-bottom: 10px;
        }

        .post-content {
            color: #666;
            margin-bottom: 15px;
            max-height: 100px;
            overflow: hidden;
        }

        .post-date {
            font-size: 0.9em;
            color: #999;
            margin-bottom: 15px;
        }

        .post-actions {
            display: flex;
            gap: 10px;
        }

        .alert {
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
            font-weight: 500;
        }

        .alert-success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }

        .alert-error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }

        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            border-radius: 15px;
            text-align: center;
        }

        .stat-number {
            font-size: 2.5em;
            font-weight: bold;
        }

        .stat-label {
            margin-top: 10px;
            opacity: 0.9;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Админ-панель блога</h1>
            <p>Управление постами для Telegram-бота</p>
        </div>

        <div class="content">
            <div id="alert-container"></div>

            <div class="stats">
                <div class="stat-card">
                    <div class="stat-number" id="total-posts">0</div>
                    <div class="stat-label">Всего постов</div>
                </div>
            </div>

            <div class="section">
                <h2>➕ Создать новый пост</h2>
                <form id="create-form">
                    <div class="form-group">
                        <label for="create-title">Заголовок:</label>
                        <input type="text" id="create-title" required>
                    </div>
                    <div class="form-group">
                        <label for="create-content">Содержимое:</label>
                        <textarea id="create-content" required></textarea>
                    </div>
                    <button type="submit" class="btn">Создать пост</button>
                </form>
            </div>

            <div class="section">
                <h2>📝 Управление постами</h2>
                <button onclick="loadPosts()" class="btn">Обновить список</button>
                <div id="posts-container" class="posts-grid"></div>
            </div>
        </div>
    </div>

    <script>
        const API_BASE = window.location.origin;

        // Показать уведомление
        function showAlert(message, type = 'success') {
            const alertContainer = document.getElementById('alert-container');
            const alert = document.createElement('div');
            alert.className = `alert alert-${type}`;
            alert.textContent = message;
            alertContainer.innerHTML = '';
            alertContainer.appendChild(alert);

            setTimeout(() => {
                alert.remove();
            }, 5000);
        }

        // Загрузить посты
        async function loadPosts() {
            try {
                const response = await fetch(`${API_BASE}/posts`);
                const posts = await response.json();

                document.getElementById('total-posts').textContent = posts.length;

                const container = document.getElementById('posts-container');
                container.innerHTML = '';

                if (posts.length === 0) {
                    container.innerHTML = '<p style="text-align: center; color: #666;">Нет постов для отображения</p>';
                    return;
                }

                posts.forEach(post => {
                    const postElement = document.createElement('div');
                    postElement.className = 'post-card';
                    postElement.innerHTML = `
                        <div class="post-title">${post.title}</div>
                        <div class="post-content">${post.content.substring(0, 150)}${post.content.length > 150 ? '...' : ''}</div>
                        <div class="post-date">📅 ${new Date(post.created_at).toLocaleString('ru-RU')}</div>
                        <div class="post-actions">
                            <button class="btn" onclick="editPost(${post.id}, '${post.title.replace(/'/g, "\'")}', '${post.content.replace(/'/g, "\'")}')">Редактировать</button>
                            <button class="btn btn-danger" onclick="deletePost(${post.id})">Удалить</button>
                        </div>
                    `;
                    container.appendChild(postElement);
                });
            } catch (error) {
                showAlert('Ошибка при загрузке постов: ' + error.message, 'error');
            }
        }

        // Создать пост
        document.getElementById('create-form').addEventListener('submit', async (e) => {
            e.preventDefault();

            const title = document.getElementById('create-title').value;
            const content = document.getElementById('create-content').value;

            try {
                const response = await fetch(`${API_BASE}/posts`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': 'Basic ' + btoa('admin:admin123')
                    },
                    body: JSON.stringify({ title, content })
                });

                if (response.ok) {
                    showAlert('Пост успешно создан!');
                    document.getElementById('create-form').reset();
                    loadPosts();
                } else {
                    const error = await response.json();
                    showAlert('Ошибка: ' + error.detail, 'error');
                }
            } catch (error) {
                showAlert('Ошибка при создании поста: ' + error.message, 'error');
            }
        });

        // Редактировать пост
        function editPost(id, title, content) {
            const newTitle = prompt('Новый заголовок:', title);
            if (newTitle === null) return;

            const newContent = prompt('Новое содержимое:', content);
            if (newContent === null) return;

            updatePost(id, newTitle, newContent);
        }

        // Обновить пост
        async function updatePost(id, title, content) {
            try {
                const response = await fetch(`${API_BASE}/posts/${id}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': 'Basic ' + btoa('admin:admin123')
                    },
                    body: JSON.stringify({ title, content })
                });

                if (response.ok) {
                    showAlert('Пост успешно обновлен!');
                    loadPosts();
                } else {
                    const error = await response.json();
                    showAlert('Ошибка: ' + error.detail, 'error');
                }
            } catch (error) {
                showAlert('Ошибка при обновлении поста: ' + error.message, 'error');
            }
        }

        // Удалить пост
        async function deletePost(id) {
            if (!confirm('Вы уверены, что хотите удалить этот пост?')) return;

            try {
                const response = await fetch(`${API_BASE}/posts/${id}`, {
                    method: 'DELETE',
                    headers: {
                        'Authorization': 'Basic ' + btoa('admin:admin123')
                    }
                });

                if (response.ok) {
                    showAlert('Пост успешно удален!');
                    loadPosts();
                } else {
                    const error = await response.json();
                    showAlert('Ошибка: ' + error.detail, 'error');
                }
            } catch (error) {
                showAlert('Ошибка при удалении поста: ' + error.message, 'error');
            }
        }

        // Загрузить посты при старте
        loadPosts();
    </script>
</body>
</html>
"""


@app.get("/", response_class=JSONResponse)
async def root():
    return {
        "message": "Blog Admin API",
        "version": "1.0.0",
        "admin_panel": "/admin",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/admin", response_class=HTMLResponse)
async def admin_panel():
    return admin_html

@app.get("/health", response_model=HealthResponse)
async def health_check():
    db_status = db.check_connection()

    if db_status:
        return HealthResponse(
            status="healthy",
            message="API и база данных работают нормально"
        )
    else:
        raise HTTPException(
            status_code=503,
            detail="Проблемы с подключением к базе данных"
        )

@app.get("/posts", response_model=List[PostResponse])
async def get_posts():
    try:
        posts = db.get_all_posts()
        for post in posts:
            dt = datetime.fromisoformat(post["created_at"])
            post["created_at"] = (dt + timedelta(hours=3)).isoformat()
        return posts
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения постов: {str(e)}")

@app.get("/posts/{post_id}", response_model=PostResponse)
async def get_post(post_id: int):
    post = db.get_post_by_id(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Пост не найден")
    return post

@app.post("/posts", response_model=PostResponse)
async def create_post(post: PostCreate, username: str = Depends(authenticate)):
    try:
        post_id = db.add_post(post.title, post.content)
        created_post = db.get_post_by_id(post_id)
        return created_post
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка создания поста: {str(e)}")

@app.put("/posts/{post_id}", response_model=PostResponse)
async def update_post(post_id: int, post: PostUpdate, username: str = Depends(authenticate)):
    existing_post = db.get_post_by_id(post_id)
    if not existing_post:
        raise HTTPException(status_code=404, detail="Пост не найден")

    success = db.update_post(post_id, post.title, post.content)
    if not success:
        raise HTTPException(status_code=500, detail="Ошибка обновления поста")

    updated_post = db.get_post_by_id(post_id)
    return updated_post

@app.delete("/posts/{post_id}")
async def delete_post(post_id: int, username: str = Depends(authenticate)):
    existing_post = db.get_post_by_id(post_id)
    if not existing_post:
        raise HTTPException(status_code=404, detail="Пост не найден")

    success = db.delete_post(post_id)
    if not success:
        raise HTTPException(status_code=500, detail="Ошибка удаления поста")

    return {"message": "Пост успешно удален"}

def main():
    db.create_tables()


    uvicorn.run(
        "api:app",
        host=API_HOST,
        port=API_PORT,
        reload=False,
        log_level="info"
    )

if __name__ == "__main__":
    main()

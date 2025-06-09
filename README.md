# Telegram-бот с API-панелью

### 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 2. Настройка бота

Установи токен

**Изменение config.py**
Откройте файл `config.py` и замените `YOUR_BOT_TOKEN_HERE` на ваш токен.

### 3. Запуск системы

**Полный запуск (бот + API):**
```bash
python run.py
```

**Только бот:**
```bash
python bot.py
```

**Только API:**
```bash
python api.py
```

## Использование

### Telegram бот
- `/start` - начать работу
- `/posts` - просмотр всех постов

### Веб-интерфейс
- Админ-панель: http://127.0.0.1:8000/admin
- Документация API: http://127.0.0.1:8000/docs
- Логин: `admin`, Пароль: `admin123`

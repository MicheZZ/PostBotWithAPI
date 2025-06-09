import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import BOT_TOKEN
from database import DatabaseManager


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
db = DatabaseManager()

def create_posts_keyboard(posts):
    builder = InlineKeyboardBuilder()

    for post in posts:
        title = post['title']
        if len(title) > 30:
            title = title[:27] + "..."

        builder.button(
            text=title,
            callback_data=f"post_{post['id']}"
        )

    builder.adjust(1)
    return builder.as_markup()

@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "Привет!\n\n"
        "Используй /posts - посмотреть все посты\n\n"
        "Для управления постами используйте веб-интерфейс API\n"
        "http://127.0.0.1:8000/admin\n\n"
        "Логин: admin, Пароль: admin123"
    )

@dp.message(Command("posts"))
async def cmd_posts(message: Message):
    try:
        posts = db.get_all_posts()

        if not posts:
            await message.answer(
                "Пока нет ни одного поста"
            )
            return

        keyboard = create_posts_keyboard(posts)
        await message.answer(
            f"Найдено постов: {len(posts)}\n\n"
            "Выбери пост для просмотра:",
            reply_markup=keyboard
        )

    except Exception as e:
        logger.error(f"Ошибка при получении постов: {e}")
        await message.answer(
            "Произошла ошибка при загрузке постов\n"
            "Попробуй позже"
        )

@dp.callback_query(F.data.startswith("post_"))
async def show_post(callback: CallbackQuery):
    try:
        post_id = int(callback.data.split("_")[1])
        post = db.get_post_by_id(post_id)

        if not post:
            await callback.message.edit_text(
                "Пост не найден. Возможно, он был удален."
            )
            return

        # Форматируем дату
        created_at = post['created_at']
        if isinstance(created_at, str):
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                formatted_date = dt.strftime("%d.%m.%Y %H:%M")
            except:
                formatted_date = created_at
        else:
            formatted_date = str(created_at)

        # Создаем кнопку "Назад"
        builder = InlineKeyboardBuilder()
        builder.button(text="Назад к списку", callback_data="back_to_posts")

        # Формируем текст поста
        post_text = (
            f"**{post['title']}**\n\n"
            f"{post['content']}\n\n"
            f"Дата создания: {formatted_date}"
        )

        await callback.message.edit_text(
            post_text,
            reply_markup=builder.as_markup(),
            parse_mode="Markdown"
        )

    except Exception as e:
        logger.error(f"Ошибка при показе поста: {e}")
        await callback.answer(
            "Произошла ошибка при загрузке поста.",
            show_alert=True
        )

@dp.callback_query(F.data == "back_to_posts")
async def back_to_posts(callback: CallbackQuery):
    try:
        posts = db.get_all_posts()

        if not posts:
            await callback.message.edit_text(
                "Пока нет ни одного поста\n\n"
            )
            return

        keyboard = create_posts_keyboard(posts)
        await callback.message.edit_text(
            f"Найдено постов: {len(posts)}\n\n"
            "Выбери пост для просмотра:",
            reply_markup=keyboard
        )

    except Exception as e:
        logger.error(f"Ошибка при возвращении к постам: {e}")
        await callback.answer(
            "Произошла ошибка при загрузке постов.",
            show_alert=True
        )

@dp.message()
async def handle_unknown_message(message: Message):
    await message.answer(
        "Неизвестная команда\n\n"
        "Доступные команды:\n"
        "/posts - посмотреть все посты\n"
        "/start - начать работу"
    )

async def main():
    try:
        db.create_tables()
        logger.info("База данных инициализирована")

        logger.info("Запуск Telegram бота...")
        await dp.start_polling(bot)

    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())

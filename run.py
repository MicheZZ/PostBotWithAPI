import asyncio
import multiprocessing
import signal
import sys
import time
import os
from config import BOT_TOKEN

def run_bot():
    print("Запуск Telegram бота...")
    try:
        import bot
        asyncio.run(bot.main())
    except Exception as e:
        print(f"Ошибка запуска бота: {e}")
        sys.exit(1)

def run_api():
    print("Запуск API сервера...")
    try:
        import api
        api.main()
    except Exception as e:
        print(f"Ошибка запуска API: {e}")
        sys.exit(1)

def signal_handler(sig, frame):
    print("\nПолучен сигнал завершения. Останавливаем процессы...")
    sys.exit(0)

def main():
    print("Запуск системы управления блогом...")
    print("=" * 50)

    if BOT_TOKEN == 'YOUR_BOT_TOKEN_HERE':
        print("Ошибка: Не установлен токен бота!")
        sys.exit(1)


    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    processes = []

    try:
        api_process = multiprocessing.Process(target=run_api, name="API-Server")
        api_process.start()
        processes.append(api_process)
        print("API сервер запущен")

        time.sleep(2)

        bot_process = multiprocessing.Process(target=run_bot, name="Telegram-Bot")
        bot_process.start()
        processes.append(bot_process)

        print("Система успешно запущена!")
        print("Документация API: http://127.0.0.1:8000/docs")
        print("Админ-панель: http://127.0.0.1:8000/admin")
        print("Логин: admin, Пароль: admin123")
        print("\nДля остановки нажмите Ctrl+C")
        print("=" * 50)


        for process in processes:
            process.join()

    except KeyboardInterrupt:
        print("\nПолучен сигнал завершения...")
    except Exception as e:
        print(f"Ошибка при запуске системы: {e}")
    finally:
        print("Завершение работы процессов...")
        for process in processes:
            if process.is_alive():
                process.terminate()
                process.join(timeout=5)
                if process.is_alive():
                    process.kill()

        print("Все процессы завершены. Пока!")

if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()

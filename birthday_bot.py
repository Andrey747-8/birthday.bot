import os
import json
import datetime
import asyncio
from dotenv import load_dotenv
from telegram import Bot
from telegram.error import TelegramError
import logging

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

# Загрузка переменных окружения
load_dotenv()

# Получение токена и ID группы из переменных окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_ID = os.getenv("GROUP_ID")

# Проверка корректности переменных окружения
if not BOT_TOKEN:
    logging.error(
        "Переменная окружения BOT_TOKEN не установлена. Прекращение работы.")
    exit(1)

if not GROUP_ID:
    logging.error(
        "Переменная окружения GROUP_ID не установлена. Прекращение работы.")
    exit(1)

# Преобразование GROUP_ID
try:
    if GROUP_ID.startswith('-100') or (GROUP_ID.lstrip('-').isdigit()
                                       and int(GROUP_ID) < 0):
        GROUP_ID = int(GROUP_ID)
    elif GROUP_ID.startswith('@'):
        GROUP_ID = GROUP_ID.lower()
    else:
        logging.error(
            f"Неверный формат GROUP_ID: {GROUP_ID}. Должен начинаться с -100, @ или быть числовым ID"
        )
        exit(1)
except Exception as e:
    logging.error(f"Ошибка обработки GROUP_ID: {e}")
    exit(1)

logging.info(f"Используется BOT_TOKEN: {BOT_TOKEN[:5]}...")
logging.info(f"Используется GROUP_ID: {GROUP_ID}")


def load_birthdays():
    try:
        with open('birthdays.json', 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        logging.error("Файл birthdays.json не найден!")
        return []
    except json.JSONDecodeError as e:
        logging.error(f"Ошибка в формате birthdays.json: {e}")
        return []
    except Exception as e:
        logging.error(f"Неожиданная ошибка при загрузке birthdays.json: {e}")
        return []


async def send_congratulation():
    birthdays = load_birthdays()
    if not birthdays:
        logging.info("Дни рождения не загружены или файл пуст.")
        return

    today = datetime.datetime.now().strftime("%d.%m")
    today_people = [
        f"{bd.get('name','')} {bd.get('surname','')}".strip()
        for bd in birthdays if bd.get("date", "") == today
    ]

    if not today_people:
        logging.info(f"Нет именинников на дату {today}.")
        return

    message = (
        f"Сегодня  День рождения отмечают: {', '.join(today_people)}\n"
        "Смирно! А теперь вольно, но только если сказал пару приятных слов своему боевому товарищу!"
    )
    logging.info(f"Попытка отправить сообщение в чат {GROUP_ID}")

    try:
        bot = Bot(token=BOT_TOKEN)
        await bot.send_message(chat_id=GROUP_ID, text=message)
        logging.info(f"Поздравления отправлены: {today_people}")
    except TelegramError as e:
        logging.error(f"Ошибка Telegram при отправке сообщения: {e}")
    except Exception as e:
        logging.error(f"Неожиданная ошибка при отправке сообщения: {e}")


async def check_birthdays():
    while True:
        try:
            await send_congratulation()
            logging.info("Ожидание следующей проверки через 24 часа...")
            await asyncio.sleep(86400)  # 24 часа
        except Exception as e:
            logging.error(f"Произошла ошибка в основном цикле: {e}")
            logging.info("Ждем 1 час перед повторной попыткой...")
            await asyncio.sleep(3600)  # 1 час


if __name__ == "__main__":
    try:
        asyncio.run(check_birthdays())
    except KeyboardInterrupt:
        logging.info("Бот остановлен вручную")
    except Exception as e:
        logging.error(f"Фатальная ошибка: {e}")


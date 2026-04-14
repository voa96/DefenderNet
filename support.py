import asyncio
import subprocess
import sys
import importlib
import logging
from datetime import datetime

# Включаем логирование для отладки
logging.basicConfig(level=logging.INFO)

required_packages = {
    'aiogram': '3.15.0',
    'requests': None,
    'aiohttp': None,
}

def install_or_upgrade_package(package, version=None):
    """Устанавливает или обновляет пакет через pip"""
    if version:
        package_spec = f"{package}=={version}"
    else:
        package_spec = package
    
    print(f"📦 Устанавливаю/обновляю {package_spec}...")
    subprocess.check_call([
        sys.executable, "-m", "pip", "install", "--upgrade", package_spec
    ])

def check_and_install():
    """Проверяет наличие библиотек и устанавливает/обновляет недостающие"""
    for package, version in required_packages.items():
        try:
            module = importlib.import_module(package)
            print(f"✅ {package} уже установлен")
            
            if version:
                installed_version = getattr(module, '__version__', None)
                if installed_version and installed_version != version:
                    print(f"⚠️ Версия {package} ({installed_version}) не соответствует требуемой ({version}). Обновляю...")
                    install_or_upgrade_package(package, version)
        except ImportError:
            print(f"❌ {package} не найден. Устанавливаю...")
            install_or_upgrade_package(package, version)

check_and_install()

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.exceptions import TelegramNetworkError


BOT_TOKEN = "8424921945:AAEJda5h4a1Na1W9kfJbNbFOElejUZdU91k" 


ADMIN_ID = 6877594405
# ============================================

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Обработчик команды /start
@dp.message(Command("start"))
async def start_command(message: types.Message):
    """Приветственное сообщение при запуске бота"""
    user_name = message.from_user.first_name or "пользователь"
    
    await message.answer(
        f"🛡️ **Добро пожаловать в службу поддержки DefenderNet, {user_name}!**\n\n"
        "📌 **Что я умею:**\n"
        "• Принимать ваши вопросы и жалобы\n"
        "• Передавать их модератору\n"
        "• Доставлять ответы от поддержки\n\n"
        "💬 **Просто напишите ваше сообщение ниже** — и модератор ответит в ближайшее время.\n\n"
        "⏱️ Обычное время ответа: до 15 минут\n\n"
        "📢 Наш канал: @DefenderNet\n"
        "🔗 Наш бот для покупки доступа: @DefenderNet_bot",
        parse_mode="Markdown"
    )

# Обработчик всех текстовых сообщений
@dp.message()
async def forward_to_admin(message: types.Message):
    """Обрабатывает все входящие сообщения"""
    user_id = message.from_user.id
    username = message.from_user.username or "без username"
    first_name = message.from_user.first_name or "без имени"
    
    # Игнорируем команду /start (она уже обработана выше)
    if message.text and message.text.startswith("/start"):
        return
    
    try:
        # Если сообщение от обычного пользователя (НЕ админа)
        if user_id != ADMIN_ID:
            # Пересылаем сообщение админу с подробной информацией
            await bot.send_message(
                ADMIN_ID,
                f"📩 **Новое сообщение в поддержку**\n\n"
                f"👤 **Пользователь:** {first_name}\n"
                f"🆔 **ID:** `{user_id}`\n"
                f"📛 **Username:** @{username}\n"
                f"🕐 **Время:** {datetime.now().strftime('%H:%M:%S %d.%m.%Y')}\n\n"
                f"💬 **Текст сообщения:**\n"
                f"\"{message.text}\"\n\n"
                f"➡️ *Чтобы ответить, нажмите Reply на это сообщение*",
                parse_mode="Markdown"
            )
            
            # Подтверждаем пользователю, что сообщение получено
            await message.answer(
                "✅ **Ваше сообщение отправлено в поддержку!**\n\n"
                "Ответ придёт сюда в этот чат. Ожидайте.",
                parse_mode="Markdown"
            )
            
            # Логируем в консоль
            print(f"📨 Получено сообщение от {first_name} (ID: {user_id}): {message.text[:50]}...")
        
        # Если сообщение от админа
        else:
            # Если админ отвечает на пересланное сообщение
            if message.reply_to_message and message.reply_to_message.text:
                text = message.reply_to_message.text
                
                # Ищем ID в формате "ID: `123456789`" или "От 123456789:"
                target_id = None
                
                # Способ 1: из Markdown формата "ID: `123456789`"
                if "ID: `" in text:
                    try:
                        id_start = text.find("ID: `") + 5
                        id_end = text.find("`", id_start)
                        target_id = int(text[id_start:id_end])
                    except (ValueError, IndexError):
                        pass
                
                # Способ 2: из старого формата "📩 От 123456789:"
                if target_id is None and "От " in text and ":\n" in text:
                    try:
                        user_id_start = text.find("От ") + 3
                        user_id_end = text.find(":\n")
                        target_id = int(text[user_id_start:user_id_end])
                    except (ValueError, IndexError):
                        pass
                
                if target_id:
                    # Отправляем ответ пользователю
                    await bot.send_message(
                        target_id,
                        f"📢 **Ответ от службы поддержки DefenderNet:**\n\n"
                        f"{message.text}\n\n"
                        f"---\n"
                        f"_Если ваш вопрос решён, просто проигнорируйте это сообщение._",
                        parse_mode="Markdown"
                    )
                    
                    # Подтверждаем админу
                    await message.answer(f"✅ Ответ успешно отправлен пользователю `{target_id}`", parse_mode="Markdown")
                    print(f"✉️ Ответ отправлен пользователю {target_id}: {message.text[:50]}...")
                else:
                    await message.answer(
                        "❌ **Не удалось определить ID пользователя.**\n\n"
                        "Убедитесь, что вы отвечаете (Reply) на сообщение, которое бот прислал вам от пользователя.\n\n"
                        "Формат сообщения должен содержать строку `ID: ` или `От `",
                        parse_mode="Markdown"
                    )
            else:
                await message.answer(
                    "ℹ️ **Чтобы ответить пользователю:**\n\n"
                    "1. Нажмите 'Ответить' (Reply) на сообщение от бота\n"
                    "2. Напишите ваш ответ\n"
                    "3. Бот сам отправит его пользователю",
                    parse_mode="Markdown"
                )
    
    except TelegramNetworkError as e:
        print(f"🌐 Ошибка сети: {e}")
        await asyncio.sleep(5)
    except Exception as e:
        print(f"⚠️ Неожиданная ошибка: {e}")
        await message.answer(f"❌ Произошла ошибка. Пожалуйста, попробуйте позже.")

async def main():
    print("=" * 60)
    print("🛡️  Бот-помощник DefenderNet запущен")
    print("=" * 60)
    print(f"📨 Админ ID: {ADMIN_ID}")
    print("⚠️ Убедитесь, что VPN выключен!")
    print("=" * 60)
    print("💡 Как работать:")
    print("   1. Пользователь пишет боту (или нажимает /start)")
    print("   2. Вам приходит сообщение с ID пользователя")
    print("   3. Нажмите 'Ответить' (Reply) и напишите ответ")
    print("   4. Бот отправит ответ пользователю от своего имени")
    print("=" * 60)
    print("🟢 Бот готов к работе...")
    print("")
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🔴 Бот остановлен")
    except Exception as e:
        print(f"\n🔴 Критическая ошибка: {e}")
import asyncio
import subprocess
import sys
import importlib
import logging

# Включаем логирование для отладки
logging.basicConfig(level=logging.INFO)

# Список библиотек с желаемыми версиями (None = последняя версия)
required_packages = {
    'aiogram': '3.15.0',  # конкретная версия
    'requests': None,      # последняя версия
    'aiohttp': None,       # последняя версия
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
    """Проверяет наличие библиотек и устанавливает/обновляет недостающие или устаревшие"""
    for package, version in required_packages.items():
        try:
            # Пытаемся импортировать
            module = importlib.import_module(package)
            print(f"✅ {package} уже установлен")
            
            # Если указана конкретная версия, проверяем её
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
from aiogram.exceptions import TelegramNetworkError


BOT_TOKEN = "8424921945:AAEJda5h4a1Na1W9kfJbNbFOElejUZdU91k" 

ADMIN_ID = 6877594405 



bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message()
async def forward_to_admin(message: types.Message):
    """Обрабатывает все входящие сообщения"""
    user_id = message.from_user.id
    
    try:
        # Если сообщение от обычного пользователя (НЕ админа)
        if user_id != ADMIN_ID:
            # Пересылаем сообщение админу
            await bot.send_message(
                ADMIN_ID,
                f"📩 От {user_id}:\n{message.text}"
            )
            # Подтверждаем пользователю, что сообщение получено
            await message.answer("✅ Ваше сообщение отправлено в поддержку. Ответ придёт сюда.")
        
        # Если сообщение от админа
        else:
            # Если админ отвечает на пересланное сообщение
            if message.reply_to_message and message.reply_to_message.text:
                text = message.reply_to_message.text
                # Ищем ID в формате "📩 От 123456789:"
                if "От " in text and ":\n" in text:
                    try:
                        user_id_start = text.find("От ") + 3
                        user_id_end = text.find(":\n")
                        target_id = int(text[user_id_start:user_id_end])
                        # Отправляем ответ пользователю
                        await bot.send_message(target_id, f"Сообщение от службы поддержки DefenderNet: {message.text}")
                        # Подтверждаем админу
                        await message.answer(f"✅ Ответ отправлен пользователю {target_id}")
                    except (ValueError, IndexError) as e:
                        await message.answer(f"❌ Ошибка при определении ID: {e}")
                else:
                    await message.answer("❌ Не могу определить ID пользователя. Убедитесь, что вы отвечаете на пересланное сообщение.")
    
    except TelegramNetworkError as e:
        print(f"🌐 Ошибка сети: {e}")
        await asyncio.sleep(5)

async def main():
    print("=" * 50)
    print("🤖 Бот-помощник DefenderNet запущен")
    print("=" * 50)
    print(f"📨 Админ ID: {ADMIN_ID}")
    print("⚠️ Убедитесь, что VPN выключен!")
    print("💡 Как работать:")
    print("   1. Пользователь пишет боту")
    print("   2. Вам приходит пересланное сообщение")
    print("   3. Нажмите 'Ответить' (Reply) и напишите ответ")
    print("   4. Бот отправит ответ пользователю")
    print("=" * 50)
    print("🟢 Бот готов к работе...")
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🔴 Бот остановлен")
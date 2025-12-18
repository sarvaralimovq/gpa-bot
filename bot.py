import os
import requests
from aiogram import Bot, Dispatcher, executor, types

# ================= НАСТРОЙКИ =================

BOT_TOKEN = "8038267516:AAG6d93_qjgH_j911QN4I8P4PZoPTKboNgY"
VT_API_KEY = "035488eaa6290d99a819389b883c2dba63b00af3b1ab457efa825924270196de"
CHANNEL_USERNAME = "@alimovsarvar2"

MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 МБ
DOWNLOAD_FOLDER = "files"

# =============================================

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

DOWNLOAD_FOLDER = "files"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# 🔒 Проверка подписки
async def check_subscription(user_id):
    try:
        member = await bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

# ▶ /start
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    if not await check_subscription(message.from_user.id):
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton(
            "📢 Подписаться",
            url=f"https://t.me/{CHANNEL_USERNAME.replace('@','')}"
        ))
        kb.add(types.InlineKeyboardButton(
            "✅ Проверить подписку",
            callback_data="check_sub"
        ))

        await message.answer(
            "❌ Чтобы пользоваться ботом, подпишись на канал:",
            reply_markup=kb
        )
    else:
        await message.answer(
            "✅ Подписка подтверждена!\n\n"
            "📂 Отправь APK или любой файл (до 20 МБ)"
        )

# 🔁 Кнопка проверки подписки
@dp.callback_query_handler(lambda c: c.data == "check_sub")
async def recheck(call: types.CallbackQuery):
    if await check_subscription(call.from_user.id):
        await call.message.edit_text(
            "✅ Подписка подтверждена!\n\n"
            "📂 Отправь файл для проверки"
        )
    else:
        await call.answer("❌ Ты ещё не подписался", show_alert=True)

# 📂 Приём файлов
@dp.message_handler(content_types=["document"])
async def scan_file(message: types.Message):
    if not await check_subscription(message.from_user.id):
        await message.answer("❌ Сначала подпишись на канал")
        return

    if message.document.file_size > MAX_FILE_SIZE:
        await message.answer(
            "❌ Файл слишком большой\n\n"
            "📦 Максимум: 20 МБ"
        )
        return

    try:
        file_info = await bot.get_file(message.document.file_id)
    except FileIsTooBig:
        await message.answer(
            "❌ Telegram не позволяет скачать файл больше 20 МБ"
        )
        return

    file_path = os.path.join(DOWNLOAD_FOLDER, message.document.file_name)
    await bot.download_file(file_info.file_path, file_path)

    await message.answer("🔍 Проверяю файл, подожди...")

    try:
        result = scan_with_virustotal(file_path)
        await message.answer(result)
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

# 🛡 VirusTotal
def scan_with_virustotal(file_path):
    url = "https://www.virustotal.com/api/v3/files"
    headers = {"x-apikey": VT_API_KEY}

    with open(file_path, "rb") as f:
        r = requests.post(url, headers=headers, files={"file": f})

    if r.status_code != 200:
        return "❌ Ошибка VirusTotal или превышен лимит API"

    data = r.json()

    try:
        stats = data["data"]["attributes"]["last_analysis_stats"]
    except KeyError:
        return (
            "⚠ Не удалось получить результат анализа\n\n"
            "Возможные причины:\n"
            "• превышен лимит API\n"
            "• файл в очереди\n"
            "• ошибка VirusTotal"
        )

    return (
        "🛡 Результат проверки:\n\n"
        f"✔ Безопасно: {stats.get('harmless', 0)}\n"
        f"⚠ Подозрительно: {stats.get('suspicious', 0)}\n"
        f"❌ Вредоносно: {stats.get('malicious', 0)}\n"
        f"❓ Неизвестно: {stats.get('undetected', 0)}\n\n"
        "⚠ Проверка не даёт 100% гарантии"
    )

# ▶ Запуск
if __name__ == "__main__":
    print("🤖 Бот запущен")
    executor.start_polling(dp, skip_updates=True)
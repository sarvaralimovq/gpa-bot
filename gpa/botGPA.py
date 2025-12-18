import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.exceptions import BotBlocked, ChatNotFound

# ================== KONFIGURATSIYA ==================
API_TOKEN = "7737349351:AAH-JwmPNkj4EQ9dYBq3ALLG8PVuCf8UTHc"
CHANNEL_USERNAME = "@alimovsarvar2"
MAX_USERS = 100
ADMIN_ID = 123456789

# Logging sozlash
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

# ================== STATES ==================
class Form(StatesGroup):
    choose_language = State()
    choose_university = State()  # YANGI STATE
    choose_calc = State()
    choose_subjects = State()
    enter_score = State()
    enter_credit = State()

# ================== GLOBAL O'ZGARUVCHILAR ==================
active_users = set()
selected_subjects_cache = {}

UNIVERSITIES = ["TATU", "TDYU", "UzMU", "SamDU", "AndMI", "Boshqa"]
SUBJECTS = ["Математика", "Физика", "Программирование", "История", "Академик письмо", "Английский", "Химия", "Биология", "География", "Литература"]

MESSAGES = {
    "uz": {
        "choose_university": "🎓 Universitetni tanlang:",
        "choose_calc": "Nima hisoblaymiz?",
        "select_subjects": "📚 Fanlarni tanlang (pastdagi tugmalar):\n✅ - tanlangan\n❌ - tanlanmagan",
        "confirm_subjects": "✅ Tasdiqlash",
        "clear_subjects": "🗑️ Tozalash",
        "enter_scores": "✍️ Barcha fanlar uchun ball kiriting (butun yoki o'nlik, masalan: 31.5 40 45):",
        "enter_credits": "✍️ Barcha fanlar uchun kredit kiriting (butun son, masalan: 4 6 3):",
        "gpa_result": "📊 Semester GPA:\n<b>GPA: {}</b>\n\nFanlar:\n{}\n\nJami ball: {}\nJami kredit: {}",
        "deadline_result": "📊 NATIJA:\n<b>Joriy reyting: {}%</b>\n\nFanlar:\n{}\n\nJami ball: {}/{}",
        "min_subject": "❌ Kamida 1 ta fan tanlang",
        "score_error": "❌ Barcha ballar son bo'lishi kerak",
        "credit_error": "❌ Barcha kreditlar butun son bo'lishi kerak",
        "count_error": "❌ {} ta {} kiritishingiz kerak",
        "limit_users": "❌ Uzr, bot hozirda {} ta foydalanuvchidan ortiq qabul qilmaydi.",
        "sub_only": "❗️Botdan foydalanish uchun kanalga obuna bo'ling:",
        "not_sub": "❌ Hali obuna emassiz",
        "welcome": "👋 Assalomu alaykum! Botimizga xush kelibsiz!\n\nBu bot orqali:\n• Semester GPA hisoblashingiz mumkin\n• Deadline uchun reyting % hisoblashingiz mumkin",
        "back": "⬅️ Orqaga",
        "cancel": "❌ Bekor qilish",
        "selected": "✅ Tanlangan fanlar:",
        "none_selected": "❌ Hech qanday fan tanlanmagan",
        "subject_added": "✅ {} qo'shildi",
        "subject_removed": "❌ {} olib tashlandi",
        "choose_lang": "🌐 Tilni tanlang / Выберите язык / Choose language:"
    },
    "ru": {
        "choose_university": "🎓 Выберите университет:",
        "choose_calc": "Что считаем?",
        "select_subjects": "📚 Выберите предметы (кнопки ниже):\n✅ - выбрано\n❌ - не выбрано",
        "confirm_subjects": "✅ Подтвердить",
        "clear_subjects": "🗑️ Очистить",
        "enter_scores": "✍️ Введите баллы по всем предметам (целые или с десятичной точкой, например: 31.5 40 45):",
        "enter_credits": "✍️ Введите кредиты по всем предметам (целые числа, например: 4 6 3):",
        "gpa_result": "📊 Semester GPA:\n<b>GPA: {}</b>\n\nПредметы:\n{}\n\nВсего баллов: {}\nВсего кредитов: {}",
        "deadline_result": "📊 РЕЗУЛЬТАТ:\n<b>Текущий рейтинг: {}%</b>\n\nПредметы:\n{}\n\nВсего баллов: {}/{}",
        "min_subject": "❌ Выберите хотя бы 1 предмет",
        "score_error": "❌ Все баллы должны быть числами",
        "credit_error": "❌ Все кредиты должны быть целыми числами",
        "count_error": "❌ Нужно ввести {} {}",
        "limit_users": "❌ Извините, бот принимает максимум {} пользователей",
        "sub_only": "❗️Для использования бота подпишитесь на канал:",
        "not_sub": "❌ Еще не подписаны",
        "welcome": "👋 Добро пожаловать в наш бот!\n\nС помощью этого бота вы можете:\n• Рассчитать Semester GPA\n• Рассчитать рейтинг % для Deadline",
        "back": "⬅️ Назад",
        "cancel": "❌ Отмена",
        "selected": "✅ Выбранные предметы:",
        "none_selected": "❌ Не выбрано ни одного предмета",
        "subject_added": "✅ {} добавлен",
        "subject_removed": "❌ {} удален",
        "choose_lang": "🌐 Выберите язык / Choose language:"
    },
    "en": {
        "choose_university": "🎓 Choose your university:",
        "choose_calc": "What to calculate?",
        "select_subjects": "📚 Select subjects (buttons below):\n✅ - selected\n❌ - not selected",
        "confirm_subjects": "✅ Confirm",
        "clear_subjects": "🗑️ Clear",
        "enter_scores": "✍️ Enter scores for all subjects (integers or decimals, e.g., 31.5 40 45):",
        "enter_credits": "✍️ Enter credits for all subjects (integers, e.g., 4 6 3):",
        "gpa_result": "📊 Semester GPA:\n<b>GPA: {}</b>\n\nSubjects:\n{}\n\nTotal score: {}\nTotal credits: {}",
        "deadline_result": "📊 RESULT:\n<b>Current rating: {}%</b>\n\nSubjects:\n{}\n\nTotal score: {}/{}",
        "min_subject": "❌ Select at least 1 subject",
        "score_error": "❌ All scores must be numbers",
        "credit_error": "❌ All credits must be integers",
        "count_error": "❌ Need to enter {} {}",
        "limit_users": "❌ Sorry, bot accepts max {} users",
        "sub_only": "❗️Subscribe to the channel to use the bot:",
        "not_sub": "❌ Not subscribed yet",
        "welcome": "👋 Welcome to our bot!\n\nWith this bot you can:\n• Calculate Semester GPA\n• Calculate rating % for Deadline",
        "back": "⬅️ Back",
        "cancel": "❌ Cancel",
        "selected": "✅ Selected subjects:",
        "none_selected": "❌ No subjects selected",
        "subject_added": "✅ {} added",
        "subject_removed": "❌ {} removed",
        "choose_lang": "🌐 Choose language:"
    }
}

# ================== YORDAMCHI FUNKSIYALAR ==================
async def check_subscribe(user_id: int) -> bool:
    """Kanal obunasini tekshirish"""
    try:
        member = await bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception as e:
        logger.error(f"Check subscribe error: {e}")
        return False

def get_subjects_keyboard(lang: str, user_id: int) -> types.ReplyKeyboardMarkup:
    """Fanlar keyboardini yaratish"""
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    user_subjects = selected_subjects_cache.get(user_id, [])
    
    for subject in SUBJECTS:
        if subject in user_subjects:
            kb.add(f"✅ {subject}")
        else:
            kb.add(f"❌ {subject}")
    
    row_buttons = []
    row_buttons.append(MESSAGES[lang]["confirm_subjects"])
    row_buttons.append(MESSAGES[lang]["clear_subjects"])
    kb.row(*row_buttons)
    
    kb.add(MESSAGES[lang]["back"], MESSAGES[lang]["cancel"])
    
    return kb

async def show_universities(message: types.Message, lang: str):
    """Universitetlar keyboardini ko'rsatish"""
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    for university in UNIVERSITIES:
        kb.add(university)
    kb.add(MESSAGES[lang]["back"])
    
    await message.answer(MESSAGES[lang]["choose_university"], reply_markup=kb)

async def show_calc_types(message: types.Message, lang: str):
    """Hisoblash turini ko'rsatish"""
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("Deadline 50 балл", "Semester GPA")
    kb.add(MESSAGES[lang]["back"])
    
    await message.answer(MESSAGES[lang]["choose_calc"], reply_markup=kb)

def format_subjects_list(subjects: list, lang: str) -> str:
    """Fanlar ro'yxatini formatlash"""
    if not subjects:
        return MESSAGES[lang]["none_selected"]
    
    text = MESSAGES[lang]["selected"] + "\n"
    for i, subject in enumerate(subjects, 1):
        text += f"{i}. {subject}\n"
    return text.strip()

# ================== ASOSIY HANDLERLAR ==================

@dp.message_handler(commands=['start', 'help'])
async def cmd_start(message: types.Message):
    """Start komandasi"""
    user_id = message.from_user.id
    
    if user_id not in active_users:
        if len(active_users) >= MAX_USERS:
            await message.answer(MESSAGES["uz"]["limit_users"].format(MAX_USERS))
            return
        active_users.add(user_id)
        logger.info(f"New user: {user_id}, Total: {len(active_users)}")
    
    # Til tanlash keyboardi
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("🇺🇿 O'zbekcha", "🇷🇺 Русский")
    kb.add("🇬🇧 English")
    
    await message.answer(MESSAGES["uz"]["welcome"], reply_markup=kb)
    await Form.choose_language.set()

@dp.message_handler(state=Form.choose_language)
async def process_language(message: types.Message, state: FSMContext):
    """Tilni tanlash"""
    lang_map = {
        "🇺🇿 O'zbekcha": "uz",
        "🇷🇺 Русский": "ru", 
        "🇬🇧 English": "en"
    }
    
    if message.text in lang_map:
        lang = lang_map[message.text]
        await state.update_data(lang=lang, user_id=message.from_user.id)
        
        if not await check_subscribe(message.from_user.id):
            kb = types.InlineKeyboardMarkup()
            kb.add(types.InlineKeyboardButton(
                "📢 Kanalga obuna bo'lish / Подписаться / Subscribe", 
                url=f"https://t.me/{CHANNEL_USERNAME.replace('@', '')}"
            ))
            kb.add(types.InlineKeyboardButton(
                "✅ Tekshirish / Проверить / Check", 
                callback_data="check_sub"
            ))
            
            await message.answer(MESSAGES[lang]["sub_only"], reply_markup=kb)
            return
        
        # Universitetlarni ko'rsatish va yangi state'ga o'tish
        await show_universities(message, lang)
        await Form.choose_university.set()
    else:
        await message.answer("Iltimos, tilni tanlang / Пожалуйста, выберите язык / Please choose language:")

@dp.callback_query_handler(lambda c: c.data == "check_sub", state="*")
async def process_check_sub(callback_query: types.CallbackQuery, state: FSMContext):
    """Obunani tekshirish"""
    data = await state.get_data()
    lang = data.get("lang", "uz")
    user_id = callback_query.from_user.id
    
    if await check_subscribe(user_id):
        await callback_query.message.delete()
        await show_universities(callback_query.message, lang)
        await Form.choose_university.set()  # ✅ YANGI STATE'GA O'TISH
        await callback_query.answer("✅ Obuna tekshirildi!", show_alert=False)
    else:
        await callback_query.answer(MESSAGES[lang]["not_sub"], show_alert=True)

@dp.message_handler(state=Form.choose_university)  # ✅ TO'G'RI STATE FILTER
async def process_university(message: types.Message, state: FSMContext):
    """Universitet tanlash"""
    data = await state.get_data()
    lang = data.get("lang", "uz")
    
    if message.text in UNIVERSITIES:
        await state.update_data(university=message.text)
        await show_calc_types(message, lang)
        await Form.choose_calc.set()
    elif message.text == MESSAGES[lang]["back"]:
        # Orqaga qaytish - til tanlashga
        await cmd_start(message)
    else:
        await message.answer("Iltimos, universitetni tanlang / Пожалуйста, выберите университет / Please choose university:")

@dp.message_handler(state=Form.choose_calc)
async def process_calc_type(message: types.Message, state: FSMContext):
    """Hisoblash turini tanlash"""
    data = await state.get_data()
    lang = data.get("lang", "uz")
    user_id = message.from_user.id
    
    if message.text in ["Deadline 50 балл", "Semester GPA"]:
        calc_type = "deadline" if "Deadline" in message.text else "gpa"
        await state.update_data(calc_type=calc_type)
        
        # Cache'dan fanlarni tozalash
        if user_id in selected_subjects_cache:
            selected_subjects_cache[user_id] = []
        
        # Fanlar keyboardini yuborish
        kb = get_subjects_keyboard(lang, user_id)
        await message.answer(MESSAGES[lang]["select_subjects"], reply_markup=kb)
        await Form.choose_subjects.set()
    elif message.text == MESSAGES[lang]["back"]:
        # Orqaga qaytish - universitet tanlashga
        await show_universities(message, lang)
        await Form.choose_university.set()
    else:
        await message.answer("Iltimos, hisoblash turini tanlang / Пожалуйста, выберите тип расчета / Please choose calculation type:")

@dp.message_handler(state=Form.choose_subjects)
async def process_subjects(message: types.Message, state: FSMContext):
    """Fanlarni tanlash"""
    data = await state.get_data()
    lang = data.get("lang", "uz")
    user_id = message.from_user.id
    
    if message.text == MESSAGES[lang]["back"]:
        await show_calc_types(message, lang)
        await Form.choose_calc.set()
        return
        
    if message.text == MESSAGES[lang]["cancel"]:
        await state.finish()
        await message.answer("❌ Amal bekor qilindi.", reply_markup=types.ReplyKeyboardRemove())
        await cmd_start(message)
        return
    
    if message.text == MESSAGES[lang]["clear_subjects"]:
        selected_subjects_cache[user_id] = []
        kb = get_subjects_keyboard(lang, user_id)
        await message.answer("✅ Barcha fanlar tozalandi!", reply_markup=kb)
        return
    
    if message.text == MESSAGES[lang]["confirm_subjects"]:
        user_subjects = selected_subjects_cache.get(user_id, [])
        
        if not user_subjects:
            await message.answer(MESSAGES[lang]["min_subject"])
            return
        
        await state.update_data(subjects=user_subjects.copy())
        subjects_text = format_subjects_list(user_subjects, lang)
        await message.answer(subjects_text)
        
        await message.answer(MESSAGES[lang]["enter_scores"], reply_markup=types.ReplyKeyboardRemove())
        await Form.enter_score.set()
        return
    
    user_subjects = selected_subjects_cache.get(user_id, [])
    subject_text = message.text[2:] if message.text.startswith(("✅ ", "❌ ")) else message.text
    
    if subject_text in SUBJECTS:
        if subject_text in user_subjects:
            user_subjects.remove(subject_text)
            response = MESSAGES[lang]["subject_removed"].format(subject_text)
        else:
            user_subjects.append(subject_text)
            response = MESSAGES[lang]["subject_added"].format(subject_text)
        
        selected_subjects_cache[user_id] = user_subjects
        kb = get_subjects_keyboard(lang, user_id)
        
        subjects_info = format_subjects_list(user_subjects, lang)
        await message.answer(f"{response}\n\n{subjects_info}", reply_markup=kb)
    else:
        await message.answer("Iltimos, pastdagi tugmalardan foydalaning / Пожалуйста, используйте кнопки ниже / Please use buttons below")

@dp.message_handler(state=Form.enter_score)
async def process_scores(message: types.Message, state: FSMContext):
    """Ballarni qabul qilish"""
    data = await state.get_data()
    lang = data.get("lang", "uz")
    subjects = data.get("subjects", [])
    
    if message.text == MESSAGES[lang]["back"]:
        user_id = message.from_user.id
        kb = get_subjects_keyboard(lang, user_id)
        await message.answer(MESSAGES[lang]["select_subjects"], reply_markup=kb)
        await Form.choose_subjects.set()
        return
    
    try:
        scores = [float(score.strip()) for score in message.text.split()]
    except ValueError:
        await message.answer(MESSAGES[lang]["score_error"])
        return
    
    if len(scores) != len(subjects):
        await message.answer(MESSAGES[lang]["count_error"].format(len(subjects), "ball"))
        return
    
    await state.update_data(scores=scores)
    
    subjects_list = "\n".join([f"{i+1}. {subjects[i]}" for i in range(len(subjects))])
    await message.answer(
        f"📋 Fanlar:\n{subjects_list}\n\n" + MESSAGES[lang]["enter_credits"]
    )
    await Form.enter_credit.set()

@dp.message_handler(state=Form.enter_credit)
async def process_credits(message: types.Message, state: FSMContext):
    """Kreditlarni qabul qilish va hisoblash"""
    data = await state.get_data()
    lang = data.get("lang", "uz")
    user_id = message.from_user.id
    
    if message.text == MESSAGES[lang]["back"]:
        await message.answer(MESSAGES[lang]["enter_scores"])
        await Form.enter_score.set()
        return
    
    try:
        credits = [int(credit.strip()) for credit in message.text.split()]
    except ValueError:
        await message.answer(MESSAGES[lang]["credit_error"])
        return
    
    subjects = data.get("subjects", [])
    scores = data.get("scores", [])
    
    if len(credits) != len(subjects):
        await message.answer(MESSAGES[lang]["count_error"].format(len(subjects), "kredit"))
        return
    
    results = []
    total_score = 0
    total_credits = sum(credits)
    
    for i in range(len(subjects)):
        subject_score = scores[i] * credits[i]
        total_score += subject_score
        results.append({
            'subject': subjects[i],
            'score': scores[i],
            'credit': credits[i],
            'total': subject_score
        })
    
    calc_type = data.get("calc_type", "gpa")
    
    if calc_type == "deadline":
        max_total = sum(50 * credit for credit in credits)
        percentage = (total_score / max_total) * 100 if max_total > 0 else 0
        
        subjects_details = ""
        for res in results:
            subjects_details += f"• {res['subject']}: {res['score']} ball, {res['credit']} kredit\n"
        
        result_text = MESSAGES[lang]["deadline_result"].format(
            round(percentage, 2),
            subjects_details.strip(),
            total_score,
            max_total
        )
    else:
        gpa = total_score / total_credits if total_credits > 0 else 0
        
        subjects_details = ""
        for res in results:
            subjects_details += f"• {res['subject']}: {res['score']} ball, {res['credit']} kredit\n"
        
        result_text = MESSAGES[lang]["gpa_result"].format(
            round(gpa, 2),
            subjects_details.strip(),
            total_score,
            total_credits
        )
    
    await message.answer(result_text, parse_mode='HTML')
    
    if user_id in selected_subjects_cache:
        del selected_subjects_cache[user_id]
    
    await state.finish()
    await show_universities(message, lang)

@dp.message_handler(commands=['stats'])
async def cmd_stats(message: types.Message):
    """Admin statistikasi"""
    if message.from_user.id != ADMIN_ID:
        return
    
    stats_text = (
        f"📊 Bot statistikasi:\n"
        f"• Faol foydalanuvchilar: {len(active_users)}\n"
        f"• Maksimum limit: {MAX_USERS}\n"
        f"• Fan tanlash cache: {len(selected_subjects_cache)}"
    )
    
    await message.answer(stats_text)

@dp.message_handler(commands=['clear_cache'])
async def cmd_clear_cache(message: types.Message):
    """Cache'ni tozalash"""
    if message.from_user.id != ADMIN_ID:
        return
    
    selected_subjects_cache.clear()
    await message.answer("✅ Barcha cache ma'lumotlari tozalandi!")

@dp.errors_handler()
async def errors_handler(update: types.Update, exception: Exception):
    """Xatolarni qayta ishlash"""
    logger.error(f"Update {update} caused error {exception}")
    return True

@dp.message_handler(commands=['about'])
async def cmd_about(message: types.Message):
    """Bot haqida ma'lumot"""
    about_text = (
        "🤖 <b>Study Calculator Bot</b>\n\n"
        "Bu bot orqali siz:\n"
        "• Semester GPA hisoblashingiz mumkin\n"
        "• Deadline reyting % hisoblashingiz mumkin\n"
        "• Turli universitetlar uchun hisob-kitob qilishingiz mumkin\n\n"
        "📞 Aloqa: @alimovsarvar2"
    )
    await message.answer(about_text, parse_mode='HTML')

@dp.message_handler()
async def unknown_message(message: types.Message):
    """Noma'lum xabarlar uchun"""
    await message.answer("⚠️ Men bu buyruqni tushunmadim. /start ni bosing yoki pastdagi tugmalardan foydalaning.")

# ================== BOTNI ISHGA TUSHIRISH ==================
if __name__ == '__main__':
    logger.info("Bot ishga tushmoqda...")
    try:
        executor.start_polling(dp, skip_updates=True)
    except KeyboardInterrupt:
        logger.info("Bot to'xtatildi.")
    except Exception as e:
        logger.error(f"Bot ishga tushirishda xatolik: {e}")
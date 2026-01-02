import asyncio
import os
import aiohttp
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
    print("ERROR: Please set BOT_TOKEN in .env file")
    exit(1)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

class UploadState(StatesGroup):
    waiting_for_expiration = State()

def get_expiration_keyboard():
    keyboard = [
        [InlineKeyboardButton(text="1 день", callback_data="exp_1d"), InlineKeyboardButton(text="7 дней", callback_data="exp_7d")],
        [InlineKeyboardButton(text="1 месяц", callback_data="exp_1m"), InlineKeyboardButton(text="Никогда", callback_data="exp_never")],
        [InlineKeyboardButton(text="Отмена", callback_data="cancel")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer("👋 Добро пожаловать в ArtyrkUpload Bot!\n\nПришли мне файл (Документ, Фото, Аудио, Видео) для загрузки.")

@dp.message(F.document | F.photo | F.video | F.audio)
async def handle_file(message: Message, state: FSMContext):
    if message.document:
        file_id = message.document.file_id
        file_name = message.document.file_name or "document"
    elif message.photo:
        file_id = message.photo[-1].file_id 
        file_name = f"photo_{file_id}.jpg"
    elif message.video:
        file_id = message.video.file_id
        file_name = message.video.file_name or f"video_{file_id}.mp4"
    elif message.audio:
        file_id = message.audio.file_id
        file_name = message.audio.file_name or f"audio_{file_id}.mp3"
    else:
        return

    await state.update_data(file_id=file_id, file_name=file_name)
    await state.set_state(UploadState.waiting_for_expiration)
    
    await message.reply(f"Файл получен: {file_name}\n\nВыберите срок действия:", reply_markup=get_expiration_keyboard())

@dp.callback_query(F.data.startswith("exp_"))
async def process_expiration(callback: CallbackQuery, state: FSMContext):
    expiration = callback.data.split("_")[1]
    data = await state.get_data()
    file_id = data.get("file_id")
    file_name = data.get("file_name")
    
    if not file_id:
        await callback.message.edit_text("Ошибка: Информация о файле потеряна. Пожалуйста, отправьте файл снова.")
        await state.clear()
        return

    await callback.message.edit_text(f"Скачиваю и загружаю файл... ({expiration})")

    try:
        file_info = await bot.get_file(file_id)
        
        temp_path = f"temp_{file_name}"
        await bot.download_file(file_info.file_path, temp_path)
        
        async with aiohttp.ClientSession() as session:
            data = aiohttp.FormData()
            data.add_field('files',
                           open(temp_path, 'rb'),
                           filename=file_name
                           )
            data.add_field('expiration', expiration)

            async with session.post(f"{API_URL}/upload", data=data) as response:
                if response.status == 200:
                    result = await response.json()
                    short_link = result.get("download_url")
                    if short_link.startswith("/"):
                        full_link = f"http://127.0.0.1:8000{short_link}"
                        
                    await callback.message.edit_text(
                        f"✅ **Успешно загружено!**\n\n"
                        f"📂 Файл: {result.get('filename')}\n"
                        f"⏳ Срок: {expiration}\n\n"
                        f"🔗 Ссылка: {full_link}\n"
                        f"🔗 Прямая: `{full_link}`",
                        parse_mode="Markdown"
                    )
                else:
                    err_text = await response.text()
                    await callback.message.edit_text(f"❌ Загрузка не удалась: {response.status} - {err_text}")

        if os.path.exists(temp_path):
            os.remove(temp_path)
            
    except Exception as e:
         await callback.message.edit_text(f"❌ Ошибка: {str(e)}")
         print(e)
    
    await state.clear()

@dp.callback_query(F.data == "cancel")
async def process_cancel(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Отменено.")
    await state.clear()

async def main():
    print("Bot started...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

##############################IMPORTS################################
from aiogram import Bot, Dispatcher, F
from aiogram.types import ChatMemberUpdated, ChatJoinRequest
from aiogram.filters.chat_member_updated import ChatMemberUpdatedFilter, JOIN_TRANSITION
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
import asyncio, logging, time
from datetime import datetime, timedelta
from aiogram.types.message_entity import MessageEntity
from config import *
import gspread
from fpdf import FPDF
from google.oauth2 import service_account
from pdfminer.high_level import extract_text
import io
from cutter import cut_image

bot = Bot(TOKEN)
dp = Dispatcher()
#####################################################################

##############################COMANDS################################
@dp.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await message.answer("Отправьте изображение или pdf-файл")

@dp.message(F.photo)
async def handle_image(message: Message, state: FSMContext):
    file_id = message.photo[-1].file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    result: io.BytesIO = await bot.download_file(file_path)
    finres = cut_image(result)
    s = ""
    if len(finres) != 3:
        pass
    else:
        for el in finres:
            s+=f"{el[1]}: {str(el[0]).replace("/","").upper()}\n"
        await message.answer(s)
    # OCR(result)
    # print(text)
    # fill_data_in_google_sheets([text])

@dp.message(F.document)
async def handle_pdf(message: Message, state: FSMContext):
    file_id = message.document.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    result: io.BytesIO = await bot.download_file(file_path)
    text = extract_text(result)
    print(text)
    # fill_data_in_google_sheets([text])

#####################################################################

##############################START##################################
async def main():
    await dp.start_polling(bot,allowed_updates=["message", "inline_query"])

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
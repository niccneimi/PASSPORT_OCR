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
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from pdfminer.high_level import extract_text
import io, re
from cutter import cut_image

bot = Bot(TOKEN)
dp = Dispatcher()

def initialize_google_sheets():
    scope = ['https://www.googleapis.com/auth/spreadsheets','https://www.googleapis.com/auth/drive','https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive.file']
    creds = ServiceAccountCredentials.from_json_keyfile_name('testpythonapi-431022-fa40e718d6f1.json', scope)
    client = gspread.authorize(creds)
    return client

def fill_data_in_google_sheets(user_id,data):
    client = initialize_google_sheets()
    sheet = client.open("inns_and_data").sheet1
    lastname = ""
    ffname = ""
    birthday = ""
    for item in data:
        if item[1] == "lastname":
            lastname = item[0]
        elif item[1] == "ffname":
            ffname = item[0]
        elif item[1] == "birthday":
            birthday = item[0]
    full_name = f"{lastname} {ffname}".strip()
    sheet.append_row([user_id, full_name.replace('/', '').upper(), birthday])

def extract_data_from_pdf_text(text):
    fio_match = re.search(r'Фамилия\s+(\S+)\s+Имя\s+(\S+)\s+Отчество\s+(\S+)', text)
    if fio_match:
        lastname, firstname, middlename = fio_match.groups()
    else:
        return None

    dob_match = re.search(r'Дата рождения\s+(\d{2}\.\d{2}\.\d{4})', text)
    if dob_match:
        dob = dob_match.group(1)
    else:
        return None

    iin_match = re.search(r'Индивидуальный Идентификационный\s+Номер\(ИИН\):\s*(\d{12})', text)
    if iin_match:
        iin = iin_match.group(1)
    else:
        return None

    return {
        'lastname': lastname,
        'firstname': firstname,
        'middlename': middlename,
        'dob': dob,
        'iin': iin
    }

def update_google_sheets_with_iin(full_name, iin):
    client = initialize_google_sheets()
    sheet = client.open("inns_and_data").sheet1
    
    cell = sheet.find(full_name)
    if cell:
        row = cell.row
        sheet.update_cell(row, 4, iin)
        return True
    return False
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
            s += f"{el[1]}: {str(el[0]).replace('/', '').upper()}\n"
        await message.answer(s)
        fill_data_in_google_sheets(message.from_user.id, finres)
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
    data = extract_data_from_pdf_text(text)
    if data:
        full_name = f"{data['lastname']} {data['firstname']} {data['middlename']}".strip().upper()
        dob = data['dob']
        iin = data['iin']
        dob_from_iin = f"{iin[4:6]}.{iin[2:4]}.20{iin[:2]}"
        if dob != dob_from_iin:
            await message.answer("Ошибка: ИНН не соответствует дате рождения.")
            return
        if update_google_sheets_with_iin(full_name, iin):
            await message.answer(f"Данные успешно обновлены:\nФИО: {full_name}\nДата рождения: {dob}\nИИН: {iin}")
        else:
            await message.answer("Не удалось найти соответствующую запись в таблице.")
    else:
        await message.answer("Не удалось извлечь необходимые данные из PDF.")

#####################################################################

##############################START##################################
async def main():
    await dp.start_polling(bot,allowed_updates=["message", "inline_query"])

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
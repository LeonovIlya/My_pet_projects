import re
import logging
import gspread

from config import GS_ID, FILENAME_GS


# подключаемся к гдоку
def connect_to_gs():
    gc = gspread.service_account(filename=FILENAME_GS)
    sh = gc.open_by_key(GS_ID)
    return sh


# получаем словарь имя_листа: его_номер в гдоке
def get_sheets_dict():
    sh = connect_to_gs()
    worksheet_list = sh.worksheets()
    ws_dict = {}
    for i in worksheet_list:
        ws_dict[i.title] = i.id
    return ws_dict


# получаем список листов в гдоке
def get_sheets_name():
    return list(get_sheets_dict().keys())


# получаем данные по адресу
def get_sheet_by_name(sheet_name, query):
    sh = connect_to_gs()
    worksheet = sh.worksheet(sheet_name)
    query_ = re.compile(r'[.\d\D\s\S\w\W]' + query.capitalize() + '([.\d\D\s\S\w\W]|$)')
    request = worksheet.findall(query_)
    result = list()
    try:
        for i in request:
            # убираем лишнее из выдачи (индекс, область, район и тд)
            re_i = re.sub(r'(^\d{6},)|(\w+\sобл,)|(\w+-\w+\sр-н,)|(\w+\sр-н,)|(\w+\sрн,)|(\s№\s)|(\sг,)',
                          "", i.value)
            result.append(
                f'*{re_i}.*\nОборудование: `{worksheet.cell(i.row, 7).value}`'
                f' - факт: `{worksheet.cell(i.row, 10).value}`'
                f' - комментарии: `{worksheet.cell(i.row, 11).value}`\n')
        return result
    except Exception as error:
        logging.info(f'{error}')
        return f'Ошибка!'


# получаем данные по номеру
def get_sheet_by_number(sheet_name, query):
    sh = connect_to_gs()
    worksheet = sh.worksheet(sheet_name)
    request = worksheet.findall(query)
    result = list()
    try:
        for i in request:
            re_i = re.sub(r'(^\d{6},)|(\w+\sобл,)|(\w+-\w+\sр-н,)|(\w+\sр-н,)|(\w+\sрн,)|(\s№\s)|(\sг,)', '', i.value)
            result.append(
                f'{re_i}. Оборудование: {worksheet.cell(i.row, 7).value} - факт: {worksheet.cell(i.row, 10).value}'
                f' - комментарии: {worksheet.cell(i.row, 11).value}\n')
        return result
    except Exception as error:
        logging.info(f'{error}')
        return f'Ошибка!'

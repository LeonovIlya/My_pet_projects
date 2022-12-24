from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup

# кластеры
ZERO_CLUSTER = InlineKeyboardButton('0', callback_data='0')
TWO_CLUSTER = InlineKeyboardButton('2', callback_data='2')

# группируем кластеры в инлайн клаву
CLUSTERS_ALL = InlineKeyboardMarkup().add(ZERO_CLUSTER, TWO_CLUSTER)

# стартовое меню для мерчендайзеров
start_menu_merch = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Планограммы')], [KeyboardButton(text='ДМП'), KeyboardButton(text='Погода')]],
    resize_keyboard=True,
    one_time_keyboard=True,
    input_field_placeholder='Выберите команду из меню')

# стартовое меню для супервайзеров
start_menu_super = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Планограммы'), KeyboardButton(text='Погода')],
    [KeyboardButton(text='ДМП'), KeyboardButton(text='Управление мерчами')]],
    resize_keyboard=True,
    one_time_keyboard=True,
    input_field_placeholder='Выберите команду из меню')

# стартовое меню для админов
start_menu_admin = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Планограммы'), KeyboardButton(text='Управление планограммами')],
    [KeyboardButton(text='ДМП'), KeyboardButton(text='Погода')],
    [KeyboardButton(text='Управление юзерами')]],
    resize_keyboard=True,
    one_time_keyboard=True,
    input_field_placeholder='Выберите команду из меню')

# кнопка для отправки геолоки
send_location = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton('Отправить геолокацию', request_location=True), KeyboardButton(text='Назад')]],
    resize_keyboard=True,
    one_time_keyboard=True,
    input_field_placeholder='Отправьте вашу геопозицию:')

# кнопки управления мерчами
manage_merch = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Добавить мерча'), KeyboardButton(text='Удалить мерча'),
     KeyboardButton(text='Редактировать мерча')],
    [KeyboardButton(text='Поиск по ФИО'), KeyboardButton(text='Список моих мерчей'), KeyboardButton(text='Назад')]],
    resize_keyboard=True,
    one_time_keyboard=True,
    input_field_placeholder='Выберите команду из меню')


# кнопки поиска дмп
dmp = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Поиск по адресу'), KeyboardButton(text='Поиск по коду ТТ')]],
    resize_keyboard=True,
    one_time_keyboard=True,
    input_field_placeholder='Выберите команду из меню')

# кнопки управления юзеров
manage_user = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Добавить юзера'), KeyboardButton(text='Удалить юзера'),
     KeyboardButton(text='Редактировать юзера')],
    [KeyboardButton(text='Поиск по ФИО'), KeyboardButton(text='Список всех юзеров'), KeyboardButton(text='Назад')]],
    resize_keyboard=True,
    one_time_keyboard=True,
    input_field_placeholder='Выберите команду из меню')

# редактирование мерча из-под супервайзера
edit_user = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Изменить ФИО'), KeyboardButton(text='Изменить пароль')],
    [KeyboardButton(text='Назад')]],
    resize_keyboard=True,
    one_time_keyboard=True,
    input_field_placeholder='Выберите команду из меню')

# редактирование юзера из-под админа
admin_edit_user = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Изменить ФИО'), KeyboardButton(text='Изменить пароль')],
    [KeyboardButton(text='Изменить уровень доступа'), KeyboardButton(text='Изменить супервайзера')],
    [KeyboardButton(text='Назад')]],
    resize_keyboard=True,
    one_time_keyboard=True,
    input_field_placeholder='Выберите команду из меню')

# универсальная кнопка назад
back = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Назад')]],
                           resize_keyboard=True,
                           one_time_keyboard=True)


# формируем инлайн клавиатуру
def get_list_inline(data):
    get_list_keyboard = InlineKeyboardMarkup()
    for i in data:
        get_list_keyboard.insert(InlineKeyboardButton(f'{i}', callback_data=f'{i}'))
    return get_list_keyboard


# формируем обычную клавиатуру
def get_list_reply(data):
    get_list_keyboard = ReplyKeyboardMarkup()
    for i in data:
        get_list_keyboard.insert(KeyboardButton(f'{i}'))
    return get_list_keyboard

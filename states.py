from aiogram.dispatcher.filters.state import StatesGroup, State


class UserState(StatesGroup):
    new_user = State()
    auth = State()

    dmp = State()
    dmp_address_search = State()
    dmp_tt_search = State()

    plan_cluster = State()
    plan_shop = State()
    plan_name = State()

    manage_merch = State()
    add_merch_set_name = State()
    add_merch_set_password = State()

    edit_merch_set_name = State()
    edit_merch_choice = State()
    edit_merch_set_new_name = State()
    edit_merch_set_new_password = State()

    delete_merch_set_name = State()

    supervisor = State()
    admin = State()

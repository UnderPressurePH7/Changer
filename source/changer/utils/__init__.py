# -*- coding: utf-8 -*-
__all__ = [
    'print_log',
    'print_error',
    'print_debug',
    'set_shared_data',
    'get_shared_data'
]

DEBUG_MODE = True

_shared_data = {
    'original_name': None,
    'new_name': None,
    'accountDBID': None
}

def print_log(log):
    print("[CHANGER]: {}".format(str(log)))

def print_error(log):
    print("[CHANGER] [ERROR]: {}".format(str(log)))

def print_debug(log):
    global DEBUG_MODE
    if DEBUG_MODE:
        print("[CHANGER] [DEBUG]: {}".format(str(log)))

def set_shared_data(key, value):
    """
    Встановлює значення в shared data.
    
    Для 'original_name' встановлює тільки один раз (щоб не перезаписати).
    Для інших ключів дозволяє оновлення.
    """
    global _shared_data
    if key == 'original_name' and _shared_data.get(key) is not None:
        # Не перезаписуємо оригінальне ім'я якщо воно вже встановлене
        print_debug("original_name already set, skipping")
        return
    _shared_data[key] = value

def get_shared_data(key):
    return _shared_data.get(key)
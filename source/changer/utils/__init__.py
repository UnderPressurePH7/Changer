# -*- coding: utf-8 -*-
__all__ = [
    'print_log',
    'print_error',
    'print_debug',


DEBUG_MODE = True

def print_log(log):
    print("[CHANGER]: {}".format(str(log)))

def print_error(log):
    print("[CHANGER] [ERROR]: {}".format(str(log)))

def print_debug(log):
    global DEBUG_MODE
    if DEBUG_MODE:
        print("[CHANGER] [DEBUG]: {}".format(str(log)))

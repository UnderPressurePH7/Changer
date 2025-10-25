# -*- coding: utf-8 -*-
from changer.utils import print_error, print_log
from changer.config import Config
from changer.accountDBID import AccountDBID
from changer.patches import apply_patches

__version__ = "0.0.6" 
__author__ = "Under_Pressure"
__copyright__ = "Copyright 2025, Under_Pressure"
__mod_name__ = "Changer"

_config = None
_account_did = None

def init():
    global _config, _account_did
    try:
        print_log('MOD {} START LOADING: v{}'.format(__mod_name__, __version__))
        _account_did = AccountDBID()
        _config = Config()
        apply_patches(_config)
        print_log('MOD {} LOADED SUCCESSFULLY'.format(__mod_name__))
    except Exception as e:
        print_error("Error initializing mod: {}".format(e))

def fini():
    global _config, _account_did
    try:
        if _config:
            _config = None
        if _account_did:
            _account_did.finalize()
            _account_did = None
        print_log('MOD {} START FINALIZING'.format(__mod_name__))
    except Exception as e:
        print_error("Error finalizing mod: {}".format(e))
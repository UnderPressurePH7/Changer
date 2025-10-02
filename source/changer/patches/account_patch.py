# -*- coding: utf-8 -*-
import BigWorld
from ..utils import print_log, print_debug, print_error

_original_init = None
_original_name = None
_config = None

def patch(config):
    global _original_init, _config
    _config = config
    
    try:
        from Account import PlayerAccount
        _original_init = PlayerAccount.__init__
        PlayerAccount.__init__ = _patched_init
        print_log("Account patched successfully")
    except Exception as e:
        print_error("Failed to patch Account: %s" % str(e))

def _patched_init(self):
    global _original_name
    _original_init(self)
    try:
        if _original_name is None:
            _original_name = self.name
        new_name = _config.load_nickname_from_config()
        self.name = new_name
        print_log("Nickname changed: %s -> %s" % (_original_name, new_name))
    except Exception as e:
        print_error("Error in patched Account.__init__: %s" % str(e))
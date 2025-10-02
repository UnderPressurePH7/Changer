# -*- coding: utf-8 -*-
import BigWorld
from ..utils import print_log, print_debug, print_error, set_shared_data

_original_init = None
_original_onBecomePlayer = None
_config = None

def patch(config):
    global _original_init, _original_onBecomePlayer, _config
    _config = config
    
    try:
        from Account import PlayerAccount
        _original_init = PlayerAccount.__init__
        PlayerAccount.__init__ = _patched_init
        
        _original_onBecomePlayer = PlayerAccount.onBecomePlayer
        PlayerAccount.onBecomePlayer = _patched_onBecomePlayer
        
        print_log("Account patched successfully")
    except Exception as e:
        print_error("Failed to patch Account: %s" % str(e))

def _patched_init(self):
    _original_init(self)

def _patched_onBecomePlayer(self):
    try:
        if hasattr(self, 'name'):
            original_name = self.name
            set_shared_data('original_name', original_name)
            new_name = _config.load_nickname_from_config()
            self.name = new_name
            print_log("Nickname changed: %s -> %s" % (original_name, new_name))
    except Exception as e:
        print_error("Error in patched Account.onBecomePlayer: %s" % str(e))
    
    _original_onBecomePlayer(self)
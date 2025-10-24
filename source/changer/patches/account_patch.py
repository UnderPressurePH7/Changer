# -*- coding: utf-8 -*-
import BigWorld
from ..utils import print_log, print_debug, print_error, set_shared_data, get_shared_data

_config = None

def patch(config):
    global _config
    _config = config
    
    try:
        from Account import PlayerAccount
        
        if hasattr(PlayerAccount, '_original_onBecomePlayer'):
            print_debug("PlayerAccount already patched, skipping")
            return
        
        original_onBecomePlayer = PlayerAccount.onBecomePlayer
        
        def patched_onBecomePlayer(self):
            try:
                if hasattr(self, 'name'):
                    original_name = self.name
                   
                    set_shared_data('original_name', original_name)
                    
                    new_name = _config.load_nickname_from_config()
                    set_shared_data('new_name', new_name)
                    
                    print_log("Original name stored: %s, will be displayed as: %s" % (original_name, new_name))
                else:
                    print_error("PlayerAccount has no 'name' attribute")
            except Exception as e:
                print_error("Error in patched Account.onBecomePlayer: %s" % str(e))
            
            return original_onBecomePlayer(self)
        
        PlayerAccount._original_onBecomePlayer = original_onBecomePlayer
        PlayerAccount.onBecomePlayer = patched_onBecomePlayer

        patch_account_name_getter(PlayerAccount)
        
        print_log("Account patched successfully")
    except ImportError:
        print_error("Failed to import Account.PlayerAccount")
    except Exception as e:
        print_error("Failed to patch Account: %s" % str(e))


def patch_account_name_getter(PlayerAccount):

    try:
        if hasattr(PlayerAccount, 'name'):
            print_debug("Account.name left unchanged (safer for server communication)")
        
        def getDisplayName(self):
            new_name = get_shared_data('new_name')
            if new_name:
                return new_name
            return self.name
        
        PlayerAccount.getDisplayName = getDisplayName
        print_debug("PlayerAccount.getDisplayName added")
        
    except Exception as e:
        print_error("Failed to patch account name getter: %s" % str(e))
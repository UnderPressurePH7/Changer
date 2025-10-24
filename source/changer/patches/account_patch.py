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
                    object.__setattr__(self, '_changer_real_name', original_name)
                    
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
        
        patch_account_name_attribute(PlayerAccount)
        
        print_log("Account patched successfully")
    except ImportError:
        print_error("Failed to import Account.PlayerAccount")
    except Exception as e:
        print_error("Failed to patch Account: %s" % str(e))


def patch_account_name_attribute(PlayerAccount):
    try:
        if hasattr(PlayerAccount, '_changer_original_getattribute'):
            print_debug("PlayerAccount.__getattribute__ already patched, skipping")
            return
        
        original_getattribute = PlayerAccount.__getattribute__
        
        def patched_getattribute(self, attr_name):

            value = original_getattribute(self, attr_name)
            
            if attr_name != 'name':
                return value
            
            try:
                new_name = get_shared_data('new_name')
                if new_name:
                    real_name = original_getattribute(self, '_changer_real_name') if hasattr(self, '_changer_real_name') else value
                    original_name = get_shared_data('original_name')
                    
                    if real_name == original_name:
                        print_debug("Account.name: returning '%s' (instead of '%s')" % (new_name, real_name))
                        return new_name
            except Exception as e:
                print_error("Error in patched __getattribute__: %s" % str(e))
            
            return value
        
        PlayerAccount._changer_original_getattribute = original_getattribute
        PlayerAccount.__getattribute__ = patched_getattribute
        print_debug("PlayerAccount.__getattribute__ patched for 'name' attribute")
        
        def getDisplayName(self):
            new_name = get_shared_data('new_name')
            return new_name if new_name else original_getattribute(self, 'name')
        
        def getRealName(self):
            if hasattr(self, '_changer_real_name'):
                return original_getattribute(self, '_changer_real_name')
            return original_getattribute(self, 'name')
        
        PlayerAccount.getDisplayName = getDisplayName
        PlayerAccount.getRealName = getRealName
        print_debug("PlayerAccount helper methods added")
        
    except Exception as e:
        print_error("Failed to patch account name attribute: %s" % str(e))

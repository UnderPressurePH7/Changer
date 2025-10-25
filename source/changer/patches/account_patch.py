# -*- coding: utf-8 -*-
import BigWorld
from ..utils import print_log, print_debug, print_error, set_shared_data, get_shared_data

_config = None

def patch(config):
    global _config
    _config = config
    
    try:
        from Account import PlayerAccount
        
        if hasattr(PlayerAccount, '_changer_correctly_patched'):
            print_debug("PlayerAccount already patched, skipping")
            return
        
        original_onBecomePlayer = PlayerAccount.onBecomePlayer
        
        def patched_onBecomePlayer(self):
            try:
                if hasattr(self, 'name'):                   
                    real_name = getattr(self, 'name', None)
                    
                    if real_name and not get_shared_data('original_name'):
                        set_shared_data('original_name', real_name)
                        print_log("Original name: %s" % real_name)
                        
                        new_name = _config.load_nickname_from_config()
                        set_shared_data('new_name', new_name)
                        print_log("New name: %s" % new_name)
                        
            except Exception as e:
                print_error("Error in onBecomePlayer: %s" % str(e))
            
            return original_onBecomePlayer(self)
                
        original_getattribute = PlayerAccount.__getattribute__
        
        def patched_getattribute(self, attr_name):
            if attr_name != 'name':
                return original_getattribute(self, attr_name)
            
            try:
                real_name = original_getattribute(self, attr_name)
                
                new_name = get_shared_data('new_name')
                if not new_name:
                    return real_name
                
                original_name = get_shared_data('original_name')
                if not original_name:
                    return real_name
                
                if real_name == original_name:
                    return new_name
                
                return real_name
                
            except Exception as e:
                print_error("Error in patched_getattribute: %s" % str(e))
                return original_getattribute(self, attr_name)
        
        original_setattr = PlayerAccount.__setattr__
        
        def patched_setattr(self, attr_name, value):
            if attr_name == 'name' and not get_shared_data('original_name'):
                set_shared_data('original_name', value)
                print_debug("Original name captured in __setattr__: %s" % value)
                
                if not get_shared_data('new_name') and _config:
                    new_name = _config.load_nickname_from_config()
                    set_shared_data('new_name', new_name)
                    print_debug("New name auto-loaded: %s" % new_name)
            
            return original_setattr(self, attr_name, value)
        
        PlayerAccount.onBecomePlayer = patched_onBecomePlayer
        PlayerAccount.__getattribute__ = patched_getattribute
        PlayerAccount.__setattr__ = patched_setattr
        
        def getDisplayName(self):
            return get_shared_data('new_name') or get_shared_data('original_name') or 'Unknown'
        
        def getRealName(self):
            return get_shared_data('original_name') or 'Unknown'
        
        PlayerAccount.getDisplayName = getDisplayName
        PlayerAccount.getRealName = getRealName
        
        PlayerAccount._changer_original_getattribute = original_getattribute
        PlayerAccount._changer_original_setattr = original_setattr
        PlayerAccount._changer_original_onBecomePlayer = original_onBecomePlayer

        print_debug("PlayerAccount patched successfully (accounting for _AccountRepository)")

    except Exception as e:
        print_error("Failed to patch PlayerAccount: %s" % str(e))
        import traceback
        print_error(traceback.format_exc())
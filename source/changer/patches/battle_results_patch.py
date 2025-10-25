# -*- coding: utf-8 -*-
from ..utils import print_debug, print_error, get_shared_data

try:
    unicode
except NameError:
    unicode = str

def patch():
    print_debug("Starting battle results patches...")
    
    patch_players_info()
    
    print_debug("Battle results patches applied")


def patch_players_info():
    try:
        from gui.battle_results.reusable.players import PlayerInfo
        
        if hasattr(PlayerInfo, '_original_realName'):
            print_debug("PlayerInfo.realName already patched, skipping")
            return
        
        original_realName_getter = PlayerInfo.realName.fget
        
        def patched_realName(self):
            original_name = original_realName_getter(self)
            
            try:
                myDBID = get_shared_data('accountDBID')
                if not myDBID:
                    return original_name
                
                if hasattr(self, 'dbID') and self.dbID == myDBID:
                    stored_original = get_shared_data('original_name')
                    new_name = get_shared_data('new_name')
                    
                    if new_name and stored_original and original_name == stored_original:
                        print_debug("Battle results: name changed in PlayerInfo.realName")
                        return new_name
                        
            except Exception as e:
                print_error("Error in patched PlayerInfo.realName: %s" % str(e))
            
            return original_name
        
        PlayerInfo._original_realName = original_realName_getter
        PlayerInfo.realName = property(patched_realName)
        print_debug("PlayerInfo.realName patched successfully")
        
    except ImportError:
        print_debug("gui.battle_results.reusable.players.PlayerInfo not available")
    except Exception as e:
        print_error("Failed to patch PlayerInfo: %s" % str(e))
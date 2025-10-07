# -*- coding: utf-8 -*-
import BigWorld
from account_helpers import getAccountDatabaseID
from ..utils import print_debug, print_error, get_shared_data

_config = None

def patch(config):
    global _config
    _config = config
    
    print_debug("Starting battle results patches...")
    
    patch_account_info_packer()
    
    print_debug("All battle results patches applied")


def patch_account_info_packer():
    try:
        from gui.battle_results.presenters.packers.user_info import AccountInfo
        print_debug("Patching AccountInfo._packNames...")
        if hasattr(AccountInfo, '_original_packNames'):
            print_debug("AccountInfo._packNames already patched, skipping")
            return
        
        original_packNames = AccountInfo._packNames
        
        @classmethod
        def patched_packNames(cls, model, playerInfo, battleResults):
            print_debug("Patched version that replaces player name with configured nickname")
            try:
                myDBID = getAccountDatabaseID()
                playerDBID = playerInfo.dbID
                
                if playerDBID == myDBID and myDBID is not None:
                    new_name = _config.load_nickname_from_config()
                    if new_name:
                        model.setUserName(new_name)
                        model.setFakeUserName(new_name)
                        model.setAnonymizer(playerInfo.isAnonymized())
                        print_debug("AccountInfo._packNames: Changed '%s' -> '%s'" % (playerInfo.realName, new_name))
                        return
                
                original_packNames(model, playerInfo, battleResults)
            except Exception as e:
                print_error("Error in patched _packNames: %s" % str(e))
                try:
                    original_packNames(model, playerInfo, battleResults)
                except:
                    pass
        
        AccountInfo._original_packNames = original_packNames
        AccountInfo._packNames = patched_packNames
        print_debug("AccountInfo._packNames patched successfully")
        
    except ImportError:
        print_debug("AccountInfo not available")
    except Exception as e:
        print_error("Failed to patch AccountInfo: %s" % str(e))
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
    patch_random_team_efficiency()
    
    print_debug("All battle results patches applied")


def patch_account_info_packer():
    try:
        from gui.battle_results.presenters.packers.user_info import AccountInfo
        
        if hasattr(AccountInfo, 'packFullUserNames'):
            original_packFullUserNames = AccountInfo.packFullUserNames
            
            @classmethod
            def patched_packFullUserNames(cls, model, vehicleSumInfo, battleResults):
                original_packFullUserNames(model, vehicleSumInfo, battleResults)
                
                try:
                    myDBID = getAccountDatabaseID()
                    playerDBID = vehicleSumInfo.player.dbID
                    
                    if playerDBID == myDBID:
                        new_name = _config.load_nickname_from_config()
                        original_name = get_shared_data('original_name')
                        
                        if hasattr(model, 'getUserName'):
                            current_name = model.getUserName()
                            if current_name == original_name:
                                model.setUserName(new_name)
                                print_debug("AccountInfo: Changed userName to '%s'" % new_name)
                        
                        if hasattr(model, 'getFullUserName'):
                            current_full = model.getFullUserName()
                            if original_name and original_name in current_full:
                                new_full = current_full.replace(original_name, new_name)
                                model.setFullUserName(new_full)
                                print_debug("AccountInfo: Changed fullUserName to '%s'" % new_full)
                except Exception as e:
                    print_error("Error in patched packFullUserNames: %s" % str(e))
            
            AccountInfo.packFullUserNames = patched_packFullUserNames
            print_debug("AccountInfo.packFullUserNames patched successfully")
            
    except ImportError:
        print_debug("AccountInfo not available")
    except Exception as e:
        print_error("Failed to patch AccountInfo: %s" % str(e))


def patch_random_team_efficiency():
    try:
        from gui.impl.lobby.battle_results.random_packers import RandomTeamEfficiency
        
        original_packTeam = RandomTeamEfficiency._packTeam
        
        @classmethod
        def patched_packTeam(cls, model, vehiclesInfoIterator, battleResults):
            original_packTeam(model, vehiclesInfoIterator, battleResults)
            
            try:
                myDBID = getAccountDatabaseID()
                new_name = _config.load_nickname_from_config()
                original_name = get_shared_data('original_name')
                
                for i in range(model.getSize()):
                    player = model.getValue(i)
                    if player and player.getDatabaseID() == myDBID:
                        userNames = player.userNames
                        if userNames:
                            if hasattr(userNames, 'getUserName'):
                                current_name = userNames.getUserName()
                                if current_name == original_name:
                                    userNames.setUserName(new_name)
                                    print_debug("RandomTeamEfficiency: Changed userName to '%s'" % new_name)
                            
                            if hasattr(userNames, 'getFullUserName'):
                                try:
                                    current_full = userNames.getFullUserName()
                                    if original_name and original_name in current_full:
                                        new_full = current_full.replace(original_name, new_name)
                                        userNames.setFullUserName(new_full)
                                        print_debug("RandomTeamEfficiency: Changed fullUserName to '%s'" % new_full)
                                except:
                                    pass
                        break
            except Exception as e:
                print_error("Error in patched _packTeam: %s" % str(e))
        
        RandomTeamEfficiency._packTeam = patched_packTeam
        print_debug("RandomTeamEfficiency._packTeam patched successfully")
        
    except ImportError:
        print_debug("RandomTeamEfficiency not available")
    except Exception as e:
        print_error("Failed to patch RandomTeamEfficiency: %s" % str(e))
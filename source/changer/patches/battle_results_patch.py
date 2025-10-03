# -*- coding: utf-8 -*-
import BigWorld
from account_helpers import getAccountDatabaseID
from ..utils import print_debug, print_error, get_shared_data

_config = None

def patch(config):
    global _config
    _config = config
    
    print_debug("Starting battle results patches...")
    
    patch_battle_results_sub_presenter()
    patch_user_name_model()
    
    print_debug("All battle results patches applied")


def patch_battle_results_sub_presenter():
    try:
        from gui.impl.lobby.battle_results.submodel_presenters.random_sub_presenter import RandomBattleResultsSubPresenter
        
        original_packBattleResults = RandomBattleResultsSubPresenter.packBattleResults
        
        def patched_packBattleResults(self, battleResults):
            result = original_packBattleResults(self, battleResults)
            
            try:

                viewModel = self._viewModel
                if not viewModel:
                    return result
                
                myDBID = getAccountDatabaseID()
                new_name = _config.load_nickname_from_config()
                original_name = get_shared_data('original_name')
                
                teamStats = viewModel.teamStats
                if teamStats:
                    allies = teamStats.getAllies()
                    if allies:
                        for i in range(allies.getSize()):
                            player = allies.getValue(i)
                            if player and player.getDatabaseID() == myDBID:
                                userNames = player.userNames
                                if userNames:
                                    if hasattr(userNames, 'getUserName'):
                                        current_name = userNames.getUserName()
                                        if current_name == original_name:
                                            userNames.setUserName(new_name)
                                            print_debug("BattleResults: Changed ally name to '%s'" % new_name)
                                    
                                    if hasattr(userNames, 'getFullUserName'):
                                        try:
                                            full_name = userNames.getFullUserName()
                                            if original_name and original_name in full_name:
                                                new_full_name = full_name.replace(original_name, new_name)
                                                userNames.setFullUserName(new_full_name)
                                                print_debug("BattleResults: Changed full name to '%s'" % new_full_name)
                                        except:
                                            pass
                                break
                    
                    enemies = teamStats.getEnemies()
                    if enemies:
                        for i in range(enemies.getSize()):
                            player = enemies.getValue(i)
                            if player and player.getDatabaseID() == myDBID:
                                userNames = player.userNames
                                if userNames and hasattr(userNames, 'getUserName'):
                                    current_name = userNames.getUserName()
                                    if current_name == original_name:
                                        userNames.setUserName(new_name)
                                        print_debug("BattleResults: Changed enemy name to '%s'" % new_name)
                                break
                
                battleInfo = viewModel.battleInfo
                if battleInfo and hasattr(battleInfo, 'getPlayerInfo'):
                    playerInfo = battleInfo.getPlayerInfo()
                    if playerInfo:
                        userNames = playerInfo.userNames
                        if userNames:
                            if hasattr(userNames, 'getUserName'):
                                current_name = userNames.getUserName()
                                if current_name == original_name:
                                    userNames.setUserName(new_name)
                                    print_debug("BattleResults: Changed playerInfo name to '%s'" % new_name)
                            
                            if hasattr(userNames, 'getFullUserName'):
                                try:
                                    full_name = userNames.getFullUserName()
                                    if original_name and original_name in full_name:
                                        new_full_name = full_name.replace(original_name, new_name)
                                        userNames.setFullUserName(new_full_name)
                                except:
                                    pass
                
            except Exception as e:
                print_error("Error in patched packBattleResults: %s" % str(e))
            
            return result
        
        RandomBattleResultsSubPresenter.packBattleResults = patched_packBattleResults
        print_debug("RandomBattleResultsSubPresenter patched successfully")
        
    except ImportError:
        print_debug("RandomBattleResultsSubPresenter not available")
    except Exception as e:
        print_error("Failed to patch RandomBattleResultsSubPresenter: %s" % str(e))


def patch_user_name_model():
    try:
        from gui.impl.gen.view_models.common.user_name_model import UserNameModel
        
        if hasattr(UserNameModel, 'setUserName'):
            original_setUserName = UserNameModel.setUserName
            
            def patched_setUserName(self, value):
                try:
                    original_player_name = get_shared_data('original_name')
                    if original_player_name and value == original_player_name:
                        new_name = _config.load_nickname_from_config()
                        print_debug("UserNameModel.setUserName: Changed '%s' -> '%s'" % (value, new_name))
                        return original_setUserName(self, new_name)
                except Exception as e:
                    print_error("Error in patched setUserName: %s" % str(e))
                
                return original_setUserName(self, value)
            
            UserNameModel.setUserName = patched_setUserName
            print_debug("UserNameModel.setUserName patched successfully")
        
        if hasattr(UserNameModel, 'setFullUserName'):
            original_setFullUserName = UserNameModel.setFullUserName
            
            def patched_setFullUserName(self, value):
                try:
                    original_player_name = get_shared_data('original_name')
                    if original_player_name and original_player_name in value:
                        new_name = _config.load_nickname_from_config()
                        value = value.replace(original_player_name, new_name)
                        print_debug("UserNameModel.setFullUserName: Changed name in '%s'" % value)
                except Exception as e:
                    print_error("Error in patched setFullUserName: %s" % str(e))
                
                return original_setFullUserName(self, value)
            
            UserNameModel.setFullUserName = patched_setFullUserName
            print_debug("UserNameModel.setFullUserName patched successfully")
            
    except ImportError:
        print_debug("UserNameModel not available")
    except Exception as e:
        print_error("Failed to patch UserNameModel: %s" % str(e))
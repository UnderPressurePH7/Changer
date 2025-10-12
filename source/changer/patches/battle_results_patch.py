# -*- coding: utf-8 -*-
import BigWorld
from account_helpers import getAccountDatabaseID
from ..utils import print_debug, print_error, get_shared_data

_config = None

def patch(config):
    global _config
    _config = config
    
    print_debug("Starting battle results patches...")
    
    patch_battle_results_formatters()
    patch_battle_results_views()
    
    print_debug("Battle results patches applied")


def patch_battle_results_formatters():
    try:
        from gui.battle_results.components import style
        
        if hasattr(style, '_original_getPlayerName'):
            print_debug("style.getPlayerName already patched")
            return
        
        if not hasattr(style, 'getPlayerName'):
            print_debug("style.getPlayerName not found")
            return
        
        original_getPlayerName = style.getPlayerName
        
        def patched_getPlayerName(playerInfo, showClan=True, showRegion=False):
            try:
                result = original_getPlayerName(playerInfo, showClan, showRegion)
                
                myDBID = getAccountDatabaseID()
                if myDBID is None:
                    return result

                player_dbid = None
                if hasattr(playerInfo, 'dbID'):
                    player_dbid = playerInfo.dbID
                elif hasattr(playerInfo, 'getDbID'):
                    player_dbid = playerInfo.getDbID()
                
                if player_dbid == myDBID:
                    new_name = _config.load_nickname_from_config()
                    if new_name:
                        original_name = get_shared_data('original_name')
                        if not original_name and hasattr(playerInfo, 'name'):
                            original_name = playerInfo.name
                        elif not original_name and hasattr(playerInfo, 'getName'):
                            original_name = playerInfo.getName()
                        
                        if original_name and original_name in result:
                            result = result.replace(original_name, new_name)
                            print_debug("style.getPlayerName: Changed '%s' to '%s'" % (original_name, new_name))
                
                return result
                
            except Exception as e:
                print_error("Error in patched getPlayerName: %s" % str(e))
                return original_getPlayerName(playerInfo, showClan, showRegion)
        
        style._original_getPlayerName = original_getPlayerName
        style.getPlayerName = patched_getPlayerName
        print_debug("style.getPlayerName patched successfully")
        
    except ImportError:
        print_debug("style components not available")
    except Exception as e:
        print_error("Failed to patch formatters: %s" % str(e))


def patch_battle_results_views():
    try:
        from gui.Scaleform.daapi.view.lobby.battle_results import BattleResultsWindow
        
        if not hasattr(BattleResultsWindow, '_populate'):
            print_debug("BattleResultsWindow._populate not found")
            return
        
        if hasattr(BattleResultsWindow, '_original_populate'):
            print_debug("BattleResultsWindow already patched")
            return
        
        original_populate = BattleResultsWindow._populate
        
        def patched_populate(self):
            try:
                original_populate(self)
                
                myDBID = getAccountDatabaseID()
                if myDBID is not None:
                    new_name = _config.load_nickname_from_config()
                    if new_name:
                        print_debug("BattleResultsWindow: Results displayed with custom name")
                
            except Exception as e:
                print_error("Error in patched BattleResultsWindow._populate: %s" % str(e))
                original_populate(self)
        
        BattleResultsWindow._original_populate = original_populate
        BattleResultsWindow._populate = patched_populate
        print_debug("BattleResultsWindow patched successfully")
        
    except ImportError:
        print_debug("BattleResultsWindow not available")
    except Exception as e:
        print_error("Failed to patch views: %s" % str(e))



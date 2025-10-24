# -*- coding: utf-8 -*-
from ..utils import print_debug, print_error, get_shared_data

try:
    unicode
except NameError:
    unicode = str

def patch():

    
    print_debug("Starting battle results patches...")
    
    patch_style_get_player_name()
    patch_players_info()
    patch_battle_results_service()
    
    print_debug("Battle results patches applied")


def patch_style_get_player_name():
    try:
        from gui.battle_results.components import style
        
        if hasattr(style, '_original_getPlayerName'):
            return
        
        original_getPlayerName = style.getPlayerName
        
        def patched_getPlayerName(playerInfo, showClan=True, showRegion=False):
            try:
                result = original_getPlayerName(playerInfo, showClan, showRegion)
                
                myDBID = get_shared_data('accountDBID')
                if myDBID is None:
                    print_debug("No myDBID found")
                    return result
                
                player_dbid = getattr(playerInfo, 'dbID', None)
                if not player_dbid and hasattr(playerInfo, 'getDbID'):
                    player_dbid = playerInfo.getDbID()
                
                if player_dbid == myDBID:
                    new_name = get_shared_data('new_name')
                    original_name = get_shared_data('original_name')
                    
                    if new_name and original_name and original_name in result:
                        result = result.replace(original_name, new_name)
                
                return result
                
            except Exception as e:
                print_error("Error in patched getPlayerName: %s" % str(e))
                return original_getPlayerName(playerInfo, showClan, showRegion)
        
        style._original_getPlayerName = original_getPlayerName
        style.getPlayerName = patched_getPlayerName
        print_debug("style.getPlayerName patched")
        
    except ImportError:
        print_debug("gui.battle_results.components.style not available")
    except Exception as e:
        print_error("Failed to apply battle results patches: %s" % str(e))

def patch_player_info_class():
    global _original_PlayerInfo_init
    
    try:
        from gui.battle_results.reusable.players import PlayerInfo
        
        if hasattr(PlayerInfo, '_original_realName'):
            return

        _original_PlayerInfo_init = PlayerInfo.__init__
        
        def patched_realName(self):
            original_name = original_realName_getter(self)
            
            try:
                myDBID = getAccountDatabaseID()
                if myDBID and self.dbID == myDBID:
                    new_name = _config.load_nickname_from_config()
                    stored_original = get_shared_data('original_name')
                    
                    if new_name and stored_original and original_name == stored_original:
                        return new_name
            except Exception as e:
                print_error("Error in patched PlayerInfo.realName: %s" % str(e))
            
            return original_name
        
        PlayerInfo._original_realName = original_realName_getter
        PlayerInfo.realName = property(patched_realName)
        print_debug("PlayerInfo.realName patched")
        
    except Exception as e:
        print_error("Failed to patch PlayerInfo class: %s" % str(e))


def patch_battle_results_service():
    try:
        from gui.battle_results.service import BattleResultsService
        
        if hasattr(BattleResultsService, '_original_postResult'):
            return
        
        original_postResult = BattleResultsService.postResult
        
        def patched_postResult(self, result, needToShowUI=True):
            try:
                myDBID = getAccountDatabaseID()
                if myDBID and result:
                    new_name = get_shared_data('new_name')
                    original_name = get_shared_data('original_name')
                    if new_name and original_name:
                        patch_result_data(result, myDBID, original_name, new_name)
            except Exception as e:
                print_error("Error in postResult: %s" % str(e))
            
            return original_postResult(self, result, needToShowUI)
        
        BattleResultsService._original_postResult = original_postResult
        BattleResultsService.postResult = patched_postResult
        print_debug("BattleResultsService.postResult patched")
        
    except Exception as e:
        print_error("Failed to patch BattleResultsService: %s" % str(e))


def patch_result_data(obj, myDBID, original_name, new_name):
    try:
        if isinstance(obj, dict):
            if obj.get('dbID') == myDBID:
                for key in ('name', 'userName', 'realName', 'fakeName', 'playerName', 'fullName'):
                    if key in obj and isinstance(obj[key], (str, unicode)) and original_name in obj[key]:
                        obj[key] = obj[key].replace(original_name, new_name)
            
            for value in obj.values():
                if isinstance(value, (dict, list, tuple)):
                    patch_result_data(value, myDBID, original_name, new_name)
        
        elif isinstance(obj, (list, tuple)):
            for item in obj:
                patch_result_data(item, myDBID, original_name, new_name)
        
        elif hasattr(obj, '__dict__'):
            if getattr(obj, 'dbID', None) == myDBID:
                for attr in ('name', 'userName', 'realName', 'fakeName', 'playerName', 'fullName'):
                    if hasattr(obj, attr):
                        value = getattr(obj, attr)
                        if isinstance(value, (str, unicode)) and original_name in value:
                            setattr(obj, attr, value.replace(original_name, new_name))
    
    except Exception as e:
        print_debug("Error in patch_result_data: %s" % str(e))

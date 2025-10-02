# -*- coding: utf-8 -*-
import BigWorld
from gui.battle_control import avatar_getter
from ..utils import print_debug, print_error

_original_fill_player = None
_original_invalidate_personal = None
_config = None
_original_player_name = None

def patch(config):
    global _config
    _config = config
    
    print_debug("Starting comprehensive battle patches...")
    
    _get_original_player_name()
    
    patch_tab_view()
    patch_arena_data_provider()
    patch_player_formatter()
    patch_vehicle_arena_info_vo()
    patch_vehicles_info_collection()
    patch_players_panel_controller()
    
    BigWorld.callback(0.5, lambda: patch_vehicle_arena_info_vo())
    BigWorld.callback(1.0, lambda: patch_vehicles_info_collection())
    BigWorld.callback(2.0, lambda: patch_vehicle_arena_info_vo())
    
    print_debug("All battle patches applied")

def _get_original_player_name():
    global _original_player_name
    try:
        player = BigWorld.player()
        if player and hasattr(player, 'name') and player.name:
            _original_player_name = player.name
            print_debug("Original player name set: %s" % _original_player_name)
        else:
            print_debug("Player not ready, retrying...")
            BigWorld.callback(1.0, _get_original_player_name)
    except Exception as e:
        print_error("Error getting original player name: %s" % str(e))
        BigWorld.callback(1.0, _get_original_player_name)

def patch_tab_view():
    global _original_fill_player, _original_invalidate_personal
    
    try:
        from gui.impl.battle.battle_page.tab_view import TabView
        _original_fill_player = TabView._fillPlayerModel
        TabView._fillPlayerModel = _patched_fill_player
        _original_invalidate_personal = TabView._invalidatePersonalInfo
        TabView._invalidatePersonalInfo = _patched_invalidate_personal
        
        print_debug("TabView patched successfully")
    except ImportError:
        print_debug("TabView not available (old WoT version?)")
    except Exception as e:
        print_error("Failed to patch TabView: %s" % str(e))

def _patched_fill_player(self, vehicleId, vehicleInfo):
    player = _original_fill_player(self, vehicleId, vehicleInfo)
    try:
        currentPlayerVehID = avatar_getter.getPlayerVehicleID()
        if player and currentPlayerVehID == vehicleId:
            new_name = _config.load_nickname_from_config()
            if hasattr(player, 'setUserName'):
                player.setUserName(new_name)
            if hasattr(player, 'setHiddenUserName'):
                player.setHiddenUserName(new_name)
            print_debug("TabView: Changed player name to '%s'" % new_name)
    except Exception as e:
        print_error("Error in patched _fillPlayerModel: %s" % str(e))
    return player

def _patched_invalidate_personal(self, player):
    _original_invalidate_personal(self, player)
    try:
        if player and hasattr(player, 'getIsCurrentPlayer') and player.getIsCurrentPlayer():
            new_name = _config.load_nickname_from_config()
            if hasattr(player, 'setUserName'):
                player.setUserName(new_name)
            if hasattr(player, 'setHiddenUserName'):
                player.setHiddenUserName(new_name)
            print_debug("TabView: Updated current player name to '%s'" % new_name)
    except Exception as e:
        print_error("Error in patched _invalidatePersonalInfo: %s" % str(e))

def patch_arena_data_provider():
    try:
        from gui.battle_control.arena_info.arena_dp import ArenaDataProvider
        
        original_getVehicleInfo = ArenaDataProvider.getVehicleInfo
        
        def patched_getVehicleInfo(self, vID=None):
            vInfo = original_getVehicleInfo(self, vID)
            if vInfo and hasattr(vInfo, 'player') and hasattr(vInfo.player, 'name'):
                if _original_player_name and vInfo.player.name == _original_player_name:
                    new_name = _config.load_nickname_from_config()
                    vInfo.player.name = new_name
                    print_debug("ArenaDataProvider: Changed name to '%s'" % new_name)
            return vInfo
        
        ArenaDataProvider.getVehicleInfo = patched_getVehicleInfo
        print_debug("ArenaDataProvider patched successfully")
    except ImportError:
        print_debug("ArenaDataProvider not available (old WoT version?)")
    except Exception as e:
        print_error("Failed to patch ArenaDataProvider: %s" % str(e))

def patch_player_formatter():
    try:
        from gui.battle_control.arena_info.player_format import PlayerFullNameFormatter
        
        original_normalize = PlayerFullNameFormatter._normalizePlayerName
        
        @staticmethod
        def patched_normalize_player_name(name):
            if _original_player_name and name == _original_player_name:
                new_name = _config.load_nickname_from_config()
                print_debug("PlayerFormatter: Changed name to '%s'" % new_name)
                return new_name
            return original_normalize(name)
        
        PlayerFullNameFormatter._normalizePlayerName = patched_normalize_player_name
        print_debug("PlayerFullNameFormatter patched successfully")
    except ImportError:
        print_debug("PlayerFullNameFormatter not available")
    except Exception as e:
        print_error("Failed to patch PlayerFullNameFormatter: %s" % str(e))

def patch_vehicle_arena_info_vo():
    try:
        from gui.battle_control.arena_info.arena_vos import VehicleArenaInfoVO, PlayerInfoVO
        
        if not _original_player_name:
            print_debug("Original player name not set yet, skipping VO patch")
            return
        
        new_name = _config.load_nickname_from_config()
        
        if hasattr(VehicleArenaInfoVO, 'getDisplayedName'):
            if not hasattr(VehicleArenaInfoVO, '_original_getDisplayedName'):
                VehicleArenaInfoVO._original_getDisplayedName = VehicleArenaInfoVO.getDisplayedName
                
                def patched_getDisplayedName(self, name=None):
                    result = VehicleArenaInfoVO._original_getDisplayedName(self, name)
                    if isinstance(result, (str, unicode)) and _original_player_name in result:
                        result = result.replace(_original_player_name, new_name)
                        print_debug("VehicleArenaInfoVO.getDisplayedName: Changed name")
                    return result
                
                VehicleArenaInfoVO.getDisplayedName = patched_getDisplayedName
                print_debug("VehicleArenaInfoVO.getDisplayedName patched")
        
        if hasattr(PlayerInfoVO, 'getPlayerLabel'):
            if not hasattr(PlayerInfoVO, '_original_getPlayerLabel'):
                PlayerInfoVO._original_getPlayerLabel = PlayerInfoVO.getPlayerLabel
                
                def patched_getPlayerLabel(self):
                    result = PlayerInfoVO._original_getPlayerLabel(self)
                    if result == _original_player_name:
                        print_debug("PlayerInfoVO.getPlayerLabel: Changed name")
                        return new_name
                    return result
                
                PlayerInfoVO.getPlayerLabel = patched_getPlayerLabel
                print_debug("PlayerInfoVO.getPlayerLabel patched")
        
        if hasattr(PlayerInfoVO, 'update'):
            if not hasattr(PlayerInfoVO, '_original_update'):
                PlayerInfoVO._original_update = PlayerInfoVO.update
                
                def patched_update(self, invalidate=0, name=None, **kwargs):
                    if name and name == _original_player_name:
                        name = new_name
                        print_debug("PlayerInfoVO.update: Changed name parameter")
                    return PlayerInfoVO._original_update(self, invalidate=invalidate, name=name, **kwargs)
                
                PlayerInfoVO.update = patched_update
                print_debug("PlayerInfoVO.update patched")

        print_debug("Arena VOs patched successfully")
    except ImportError:
        print_debug("Arena VOs not available")
    except Exception as e:
        print_error("Failed to patch Arena VOs: %s" % str(e))

def patch_vehicles_info_collection():
    try:
        from gui.battle_control.arena_info.vos_collections import VehiclesInfoCollection
        
        if not _original_player_name:
            print_debug("Original player name not set yet, skipping collection patch")
            return
        
        new_name = _config.load_nickname_from_config()
        
        if not hasattr(VehiclesInfoCollection, '_original_iterator'):
            VehiclesInfoCollection._original_iterator = VehiclesInfoCollection.iterator
            
            def patched_iterator(self, arenaDP):
                for vInfoVO in VehiclesInfoCollection._original_iterator(self, arenaDP):
                    if (hasattr(vInfoVO, 'player') and 
                        hasattr(vInfoVO.player, 'name') and
                        vInfoVO.player.name == _original_player_name):
                        vInfoVO.player.name = new_name
                        print_debug("VehiclesInfoCollection.iterator: Changed name")
                    yield vInfoVO
            
            VehiclesInfoCollection.iterator = patched_iterator
            print_debug("VehiclesInfoCollection patched successfully")
    except ImportError:
        print_debug("VehiclesInfoCollection not available")
    except Exception as e:
        print_error("Failed to patch VehiclesInfoCollection: %s" % str(e))

def patch_players_panel_controller():
    try:
        from gui.battle_control.controllers.players_panel_ctrl import PlayersPanelController
        
        if not hasattr(PlayersPanelController, '_addPlayerInfo'):
            print_debug("PlayersPanelController._addPlayerInfo method not found")
            return
        
        original_addPlayerInfo = PlayersPanelController._addPlayerInfo
        
        def patched_addPlayerInfo(self, vID, vInfo):
            if vInfo and hasattr(vInfo, 'player') and hasattr(vInfo.player, 'name'):
                if _original_player_name and vInfo.player.name == _original_player_name:
                    new_name = _config.load_nickname_from_config()
                    vInfo.player.name = new_name
                    print_debug("PlayersPanelController: Changed player name")
            return original_addPlayerInfo(self, vID, vInfo)
        
        PlayersPanelController._addPlayerInfo = patched_addPlayerInfo
        print_debug("PlayersPanelController patched successfully")
    except ImportError:
        print_debug("PlayersPanelController not available")
    except Exception as e:
        print_error("Failed to patch PlayersPanelController: %s" % str(e))
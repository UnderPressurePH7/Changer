# -*- coding: utf-8 -*-
import BigWorld
from gui.battle_control import avatar_getter
from ..utils import print_debug, print_error, get_shared_data

try:
    unicode
except NameError:
    unicode = str

_original_fill_player = None
_original_invalidate_personal = None

def patch():
    
    print_debug("Starting comprehensive battle patches...")
    
    patch_tab_view()
    patch_player_formatter()
    BigWorld.callback(0.5, lambda: patch_vehicle_arena_info_vo())
    
    print_debug("Battle patches applied")

def patch_tab_view():
    try:
        from gui.impl.battle.battle_page.tab_view import TabView
        
        if hasattr(TabView, '_original_fillPlayerModel'):
            print_debug("TabView already patched, skipping")
            return
        
        original_fill_player = TabView._fillPlayerModel
        
        def patched_fill_player(self, vehicleId, vehicleInfo):
            player = original_fill_player(self, vehicleId, vehicleInfo)
            try:
                currentPlayerVehID = avatar_getter.getPlayerVehicleID()
                if player and currentPlayerVehID == vehicleId:
                    new_name = get_shared_data('new_name')
                    if hasattr(player, 'setUserName'):
                        player.setUserName(new_name)
                    if hasattr(player, 'setHiddenUserName'):
                        player.setHiddenUserName(new_name)
                    print_debug("Battle: name changed in TabView")
            except Exception as e:
                print_error("Error in patched _fillPlayerModel: %s" % str(e))
            return player
        
        TabView._original_fillPlayerModel = original_fill_player
        TabView._fillPlayerModel = patched_fill_player
        print_debug("TabView patched successfully")
        
    except ImportError:
        print_debug("TabView not available")
    except Exception as e:
        print_error("Failed to patch TabView: %s" % str(e))


def patch_player_formatter():
    try:
        from gui.battle_control.arena_info.player_format import PlayerFullNameFormatter
        
        if hasattr(PlayerFullNameFormatter, '_original_normalizePlayerName'):
            print_debug("PlayerFullNameFormatter already patched, skipping")
            return
        
        original_normalize = PlayerFullNameFormatter._normalizePlayerName
        
        @staticmethod
        def patched_normalize_player_name(name):
            original_player_name = get_shared_data('original_name')
            if original_player_name and name == original_player_name:
                new_name = get_shared_data('new_name')
                print_debug("Battle: name normalized to '%s'" % new_name)
                return new_name
            return original_normalize(name)
        
        PlayerFullNameFormatter._original_normalizePlayerName = original_normalize
        PlayerFullNameFormatter._normalizePlayerName = patched_normalize_player_name
        print_debug("PlayerFullNameFormatter patched successfully")
        
    except ImportError:
        print_debug("PlayerFullNameFormatter not available")
    except Exception as e:
        print_error("Failed to patch PlayerFullNameFormatter: %s" % str(e))

def patch_vehicle_arena_info_vo():
    try:
        from gui.battle_control.arena_info.arena_vos import VehicleArenaInfoVO, PlayerInfoVO
        
        original_player_name = get_shared_data('original_name')
        if not original_player_name:
            print_debug("No original_name, skipping Arena VOs patch")
            return
        
        new_name = get_shared_data('new_name')
        
        if hasattr(VehicleArenaInfoVO, 'getDisplayedName') and not hasattr(VehicleArenaInfoVO, '_original_getDisplayedName'):
            VehicleArenaInfoVO._original_getDisplayedName = VehicleArenaInfoVO.getDisplayedName
            
            def patched_getDisplayedName(self, name=None):
                result = VehicleArenaInfoVO._original_getDisplayedName(self, name)
                orig_name = get_shared_data('original_name')
                if isinstance(result, (str, unicode)) and orig_name and orig_name in result:
                    result = result.replace(orig_name, new_name)
                    print_debug("Battle: name changed in VehicleArenaInfoVO")
                return result
            
            VehicleArenaInfoVO.getDisplayedName = patched_getDisplayedName
            print_debug("VehicleArenaInfoVO.getDisplayedName patched successfully")
        
        if hasattr(PlayerInfoVO, 'getPlayerLabel') and not hasattr(PlayerInfoVO, '_original_getPlayerLabel'):
            PlayerInfoVO._original_getPlayerLabel = PlayerInfoVO.getPlayerLabel
            
            def patched_getPlayerLabel(self):
                result = PlayerInfoVO._original_getPlayerLabel(self)
                orig_name = get_shared_data('original_name')
                if result == orig_name:
                    print_debug("Battle: name changed in PlayerInfoVO.getPlayerLabel")
                    return new_name
                return result
            
            PlayerInfoVO.getPlayerLabel = patched_getPlayerLabel
            print_debug("PlayerInfoVO.getPlayerLabel patched successfully")

    except ImportError:
        print_debug("Arena VOs not available")
    except Exception as e:
        print_error("Failed to patch Arena VOs: %s" % str(e))
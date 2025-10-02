from ..utils import print_debug, print_error

_original_fill_player = None
_original_invalidate_personal = None
_config = None

def patch(config):
    global _original_fill_player, _original_invalidate_personal, _config
    _config = config
    
    try:
        from gui.impl.battle.battle_page.tab_view import TabView
        _original_fill_player = TabView._fillPlayerModel
        TabView._fillPlayerModel = _patched_fill_player
        
        _original_invalidate_personal = TabView._invalidatePersonalInfo
        TabView._invalidatePersonalInfo = _patched_invalidate_personal

        print_debug("TabView patched successfully")
    except Exception as e:
        print_error("Failed to patch TabView: %s" % str(e))

def _patched_fill_player(self, vehicleId, vehicleInfo):
    player = _original_fill_player(self, vehicleId, vehicleInfo)
    try:
        import BigWorld
        player_vehicle_id = BigWorld.player().vehicleID if hasattr(BigWorld.player(), 'vehicleID') else None
        if player and player_vehicle_id == vehicleId:
            new_name = _config.load_nickname_from_config()
            player.setUserName(new_name)
            player.setHiddenUserName(new_name)
            print_debug("Battle: Changed player name to '%s'" % new_name)
    except Exception as e:
        print_error("Error in patched _fillPlayerModel: %s" % str(e))
    return player

def _patched_invalidate_personal(self, player):
    _original_invalidate_personal(self, player)
    try:
        import BigWorld
        if player and player.getIsCurrentPlayer():
            new_name = _config.load_nickname_from_config()
            player.setUserName(new_name)
            player.setHiddenUserName(new_name)
            print_debug("Battle: Updated current player name to '%s'" % new_name)
    except Exception as e:
        print_error("Error in patched _invalidatePersonalInfo: %s" % str(e))
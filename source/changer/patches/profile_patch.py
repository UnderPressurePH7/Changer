# -*- coding: utf-8 -*-
from ..utils import print_debug, print_error

_original_populate_page = None
_original_populate_window = None
_config = None

def patch(config):
    global _original_populate_page, _original_populate_window, _config
    _config = config
    
    try:
        from gui.Scaleform.daapi.view.lobby.profile.ProfilePage import ProfilePage
        _original_populate_page = ProfilePage._populate
        ProfilePage._populate = _patched_populate_page
        print_debug("ProfilePage patched successfully")
    except Exception as e:
        print_error("Failed to patch ProfilePage: %s" % str(e))
    
    try:
        from gui.Scaleform.daapi.view.lobby.profile.ProfileWindow import ProfileWindow
        _original_populate_window = ProfileWindow._populate
        ProfileWindow._populate = _patched_populate_window
        print_debug("ProfileWindow patched successfully")
    except Exception as e:
        print_error("Failed to patch ProfileWindow: %s" % str(e))

def _patched_populate_page(self):
    _original_populate_page(self)
    try:
        import BigWorld
        new_name = _config.load_nickname_from_config()
        player = BigWorld.player()
        if player and hasattr(player, 'name'):
            player.name = new_name
            print_debug("ProfilePage: Changed player name to '%s'" % new_name)
    except Exception as e:
        print_error("Error in patched ProfilePage._populate: %s" % str(e))

def _patched_populate_window(self):
    _original_populate_window(self)
    try:
        import BigWorld
        new_name = _config.load_nickname_from_config()
        player = BigWorld.player()
        if player and hasattr(player, 'name'):
            original_name = self._ProfileWindow__userName
            if player.databaseID == self._ProfileWindow__databaseID:
                self._ProfileWindow__userName = new_name
                print_debug("ProfileWindow: Changed userName from '%s' to '%s'" % (original_name, new_name))
    except Exception as e:
        print_error("Error in patched ProfileWindow._populate: %s" % str(e))
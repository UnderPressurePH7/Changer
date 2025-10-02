from ..utils import print_debug, print_error

_original_make_user = None
_original_make_player = None
_config = None

def patch(config):
    global _original_make_user, _original_make_player, _config
    _config = config
    
    try:
        import gui.Scaleform.daapi.view.lobby.rally.vo_converters as vo_converters
        
        _original_make_user = vo_converters.makeUserVO
        vo_converters.makeUserVO = _patched_make_user
        
        _original_make_player = vo_converters.makePlayerVO
        vo_converters.makePlayerVO = _patched_make_player
        
        print_debug("VO converters patched successfully")
    except Exception as e:
        print_error("Failed to patch VO converters: %s" % str(e))

def _patched_make_user(user, colorGetter, isPlayerSpeaking=False, lobbyContext=None):
    vo = _original_make_user(user, colorGetter, isPlayerSpeaking, lobbyContext)
    try:
        import BigWorld
        if user and BigWorld.player() and user.getID() == BigWorld.player().databaseID:
            new_name = _config.load_nickname_from_config()
            vo['userName'] = new_name
            vo['fullName'] = new_name
            print_debug("VO: Changed user name to '%s'" % new_name)
    except Exception as e:
        print_error("Error in patched makeUserVO: %s" % str(e))
    return vo

def _patched_make_player(pInfo, user, colorGetter, isPlayerSpeaking=False, isIncludeAccountWTR=False):
    vo = _original_make_player(pInfo, user, colorGetter, isPlayerSpeaking, isIncludeAccountWTR)
    try:
        import BigWorld
        if pInfo and BigWorld.player() and pInfo.dbID == BigWorld.player().databaseID:
            new_name = _config.load_nickname_from_config()
            vo['userName'] = new_name
            vo['fullName'] = new_name
            print_debug("VO: Changed player name to '%s'" % new_name)
    except Exception as e:
        print_error("Error in patched makePlayerVO: %s" % str(e))
    return vo
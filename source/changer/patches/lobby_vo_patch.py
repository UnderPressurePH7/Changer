# -*- coding: utf-8 -*-
from ..utils import print_debug, print_error, get_shared_data

_original_make_user = None
_original_make_player = None
_config = None

def patch(config):
    global _original_make_user, _original_make_player, _config
    _config = config
    
    print_debug("Starting VO patches...")
    patch_rally_vo_converters()
    patch_user_cm_handler()
    patch_prebattle_vo()
    print_debug("All VO patches applied")

def patch_rally_vo_converters():
    global _original_make_user, _original_make_player
    
    try:
        from gui.Scaleform.daapi.view.lobby.rally import vo_converters
        
        _original_make_user = vo_converters.makeUserVO
        vo_converters.makeUserVO = _patched_make_user
        
        _original_make_player = vo_converters.makePlayerVO
        vo_converters.makePlayerVO = _patched_make_player
        
        print_debug("Rally VO converters patched successfully")
    except ImportError:
        print_debug("Rally VO converters not available")
    except Exception as e:
        print_error("Failed to patch rally VO converters: %s" % str(e))

def _patched_make_user(user, colorGetter, isPlayerSpeaking=False, lobbyContext=None):
    vo = _original_make_user(user, colorGetter, isPlayerSpeaking, lobbyContext)
    try:
        import BigWorld
        if user and BigWorld.player() and user.getID() == BigWorld.player().databaseID:
            new_name = _config.load_nickname_from_config()
            vo['userName'] = new_name
            vo['fullName'] = new_name
            print_debug("Rally VO: Changed user name to '%s'" % new_name)
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
            print_debug("Rally VO: Changed player name to '%s'" % new_name)
    except Exception as e:
        print_error("Error in patched makePlayerVO: %s" % str(e))
    return vo

def patch_user_cm_handler():
    try:
        from gui.Scaleform.daapi.view.lobby.user_cm_handlers import BaseUserCMHandler
        
        if not hasattr(BaseUserCMHandler, '_makeVO'):
            print_debug("BaseUserCMHandler._makeVO not found")
            return
        
        original_makeVO = BaseUserCMHandler._makeVO
        
        def patched_makeVO(self, *args, **kwargs):
            vo = original_makeVO(self, *args, **kwargs)
            
            try:
                import BigWorld
                player = BigWorld.player()
                
                if player and isinstance(vo, dict):
                    original_player_name = get_shared_data('original_name')
                    if vo.get('dbID') == player.databaseID or (original_player_name and vo.get('userName') == original_player_name):
                        new_name = _config.load_nickname_from_config()
                        vo['userName'] = new_name
                        
                        if 'clanAbbrev' in vo and vo['clanAbbrev']:
                            vo['fullName'] = '[%s] %s' % (vo['clanAbbrev'], new_name)
                        else:
                            vo['fullName'] = new_name
                        
                        print_debug("User CM VO: Changed userName to '%s'" % new_name)
            except Exception as e:
                print_error("Error in patched BaseUserCMHandler._makeVO: %s" % str(e))
            
            return vo
        
        BaseUserCMHandler._makeVO = patched_makeVO
        print_debug("BaseUserCMHandler patched successfully")
    except ImportError:
        print_debug("BaseUserCMHandler not available")
    except Exception as e:
        print_error("Failed to patch BaseUserCMHandler: %s" % str(e))

def patch_prebattle_vo():
    try:
        from gui.prb_control.formatters import getPrebattleFullDescription
        
        original_getPrebattleFullDescription = getPrebattleFullDescription
        
        def patched_getPrebattleFullDescription(unitIdx, creator, creatorName, **kwargs):
            try:
                import BigWorld
                player = BigWorld.player()
                
                original_player_name = get_shared_data('original_name')
                if player and original_player_name and creatorName == original_player_name:
                    new_name = _config.load_nickname_from_config()
                    print_debug("Prebattle VO: Changed creator name to '%s'" % new_name)
                    return original_getPrebattleFullDescription(unitIdx, creator, new_name, **kwargs)
            except Exception as e:
                print_error("Error in patched getPrebattleFullDescription: %s" % str(e))
            
            return original_getPrebattleFullDescription(unitIdx, creator, creatorName, **kwargs)
        
        import gui.prb_control.formatters as formatters_module
        formatters_module.getPrebattleFullDescription = patched_getPrebattleFullDescription
        print_debug("Prebattle VO patched successfully")
    except ImportError:
        print_debug("Prebattle formatters not available")
    except Exception as e:
        print_error("Failed to patch prebattle VO: %s" % str(e))
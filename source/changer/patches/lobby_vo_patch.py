# -*- coding: utf-8 -*-
from ..utils import print_debug, print_error, get_shared_data

def patch():
    print_debug("Starting lobby VO patches...")
    
    patch_rally_vo_converters()
    patch_user_roster()
    patch_prebattle_vo()
    
    print_debug("Lobby VO patches applied")


def patch_rally_vo_converters():
    try:
        from gui.Scaleform.daapi.view.lobby.rally import vo_converters
        
        if hasattr(vo_converters, '_original_makeUserVO'):
            print_debug("Rally VO converters already patched, skipping")
            return
        
        original_make_user = vo_converters.makeUserVO
        
        def patched_make_user(user, colorGetter, isPlayerSpeaking=False, lobbyContext=None):
            vo = original_make_user(user, colorGetter, isPlayerSpeaking, lobbyContext)
            
            try:
                import BigWorld
                if user and BigWorld.player():
                    myDBID = get_shared_data('accountDBID')
                    if myDBID and user.getID() == myDBID:
                        new_name = get_shared_data('new_name')
                        vo['userName'] = new_name
                        vo['fullName'] = new_name
                        print_debug("Lobby: name changed in Rally VO")
            
            except Exception as e:
                print_error("Error in patched makeUserVO: %s" % str(e))
            
            return vo
        
        vo_converters._original_makeUserVO = original_make_user
        vo_converters.makeUserVO = patched_make_user
        print_debug("Rally VO converters patched successfully")
        
    except ImportError:
        print_debug("Rally VO converters not available")
    except Exception as e:
        print_error("Failed to patch rally VO converters: %s" % str(e))


def patch_user_roster():
    try:
        from gui.Scaleform.daapi.view.lobby.user_cm_handlers import USER_ACTION_ID
        from gui.prb_control.formatters import getPrebattleFullDescription
        
        print_debug("User roster formatters checked (function-based, patched via other means)")
        
    except ImportError:
        print_debug("User roster formatters not available")
    except Exception as e:
        print_error("Error in patch_user_roster: %s" % str(e))


def patch_prebattle_vo():
    try:
        from gui.prb_control.formatters.prb_formatters import PrebattleFormatter
        
        if hasattr(PrebattleFormatter, '_original_getPlayerString'):
            print_debug("PrebattleFormatter already patched, skipping")
            return
        
        if hasattr(PrebattleFormatter, '_getPlayerString'):
            original_getPlayerString = PrebattleFormatter._getPlayerString
            
            @staticmethod
            def patched_getPlayerString(name, rating=None, readyState=None):
                try:
                    original_name = get_shared_data('original_name')
                    if original_name and name == original_name:
                        new_name = get_shared_data('new_name')
                        return original_getPlayerString(new_name, rating, readyState)
                except Exception as e:
                    print_error("Error in patched getPlayerString: %s" % str(e))
                
                return original_getPlayerString(name, rating, readyState)
            
            PrebattleFormatter._original_getPlayerString = original_getPlayerString
            PrebattleFormatter._getPlayerString = patched_getPlayerString
            print_debug("PrebattleFormatter patched successfully")
        
    except ImportError:
        print_debug("PrebattleFormatter not available")
    except Exception as e:
        print_error("Failed to patch PrebattleFormatter: %s" % str(e))
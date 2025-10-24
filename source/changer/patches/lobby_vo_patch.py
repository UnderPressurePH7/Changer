# -*- coding: utf-8 -*-
from ..utils import print_debug, print_error, get_shared_data

def patch():
    
    print_debug("Starting lobby VO patches...")
    patch_rally_vo_converters()
    patch_user_cm_handler()
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
                if user and BigWorld.player() and user.getID() == get_shared_data('accountDBID'):
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

def patch_user_cm_handler():
    try:
        from gui.Scaleform.daapi.view.lobby.user_cm_handlers import BaseUserCMHandler
        
        if not hasattr(BaseUserCMHandler, '_makeVO'):
            print_debug("BaseUserCMHandler._makeVO not found")
            return
        
        if hasattr(BaseUserCMHandler, '_original_makeVO'):
            print_debug("BaseUserCMHandler already patched, skipping")
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
                        new_name = get_shared_data('new_name')
                        vo['userName'] = new_name
                        
                        if 'clanAbbrev' in vo and vo['clanAbbrev']:
                            vo['fullName'] = '[%s] %s' % (vo['clanAbbrev'], new_name)
                        else:
                            vo['fullName'] = new_name
                        
                        print_debug("Lobby: name changed in context menu")
            except Exception as e:
                print_error("Error in patched BaseUserCMHandler._makeVO: %s" % str(e))
            
            return vo
        
        BaseUserCMHandler._original_makeVO = original_makeVO
        BaseUserCMHandler._makeVO = patched_makeVO
        print_debug("BaseUserCMHandler patched successfully")
        
    except ImportError:
        print_debug("BaseUserCMHandler not available")
    except Exception as e:
        print_error("Failed to patch BaseUserCMHandler: %s" % str(e))
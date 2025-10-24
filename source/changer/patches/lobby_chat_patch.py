# -*- coding: utf-8 -*-
import BigWorld
from ..utils import print_debug, print_error, get_shared_data

def patch():
    
    print_debug("Starting lobby chat patches...")
    
    patch_lobby_context()
    patch_lobby_header()
    patch_messenger()
    
    print_debug("Lobby chat patches applied")

def patch_lobby_context():
    try:
        from gui.shared.personality import ServicesLocator
        
        if hasattr(ServicesLocator.lobbyContext, '_original_getPlayerFullName'):
            print_debug("lobbyContext.getPlayerFullName already patched, skipping")
            return
        
        original_getPlayerFullName = ServicesLocator.lobbyContext.getPlayerFullName
        
        def patched_getPlayerFullName(pName, clanInfo=None, clanAbbrev=None, regionCode=None, pDBID=None):
            try:
                original_player_name = get_shared_data('original_name')
                if original_player_name and pName == original_player_name:
                    new_name = get_shared_data('new_name')
                    print_debug("Lobby: name changed in getPlayerFullName")
                    
                    if clanAbbrev:
                        return '[%s] %s' % (clanAbbrev, new_name)
                    return new_name
                
                return original_getPlayerFullName(pName, clanInfo, clanAbbrev, regionCode, pDBID)
            except Exception as e:
                print_error("Error in getPlayerFullName: %s" % str(e))
                return original_getPlayerFullName(pName, clanInfo, clanAbbrev, regionCode, pDBID)
        
        ServicesLocator.lobbyContext._original_getPlayerFullName = original_getPlayerFullName
        ServicesLocator.lobbyContext.getPlayerFullName = patched_getPlayerFullName
        print_debug("lobbyContext.getPlayerFullName patched successfully")
        
    except ImportError:
        print_debug("ServicesLocator.lobbyContext not available")
    except Exception as e:
        print_error("Failed to patch lobbyContext: %s" % str(e))


def patch_lobby_header():
    try:
        from gui.Scaleform.daapi.view.lobby.header.LobbyHeader import LobbyHeader
        
        if hasattr(LobbyHeader, '_original_setPlayerInfo'):
            print_debug("LobbyHeader.__setPlayerInfo already patched, skipping")
            return
        
        original_setPlayerInfo = LobbyHeader._LobbyHeader__setPlayerInfo
        
        def patched_setPlayerInfo(instance, tooltip, tooltipType, tooltipArgs=None, warningIcon=False, userVO=None):
            try:
                if userVO:
                    original_player_name = get_shared_data('original_name')
                    if original_player_name and userVO.get('userName') == original_player_name:
                        new_name = get_shared_data('new_name')
                        clanAbbrev = userVO.get('clanAbbrev', None)
                        
                        userVO['userName'] = new_name
                        userVO['fullName'] = new_name if not clanAbbrev else '[%s] %s' % (clanAbbrev, new_name)
                        
                        print_debug("Lobby: name changed in header")
                
                return original_setPlayerInfo(instance, tooltip, tooltipType, tooltipArgs, warningIcon, userVO)
            except Exception as e:
                print_error("Error in setPlayerInfo: %s" % str(e))
                return original_setPlayerInfo(instance, tooltip, tooltipType, tooltipArgs, warningIcon, userVO)
        
        LobbyHeader._original_setPlayerInfo = original_setPlayerInfo
        LobbyHeader._LobbyHeader__setPlayerInfo = patched_setPlayerInfo
        print_debug("LobbyHeader.__setPlayerInfo patched successfully")
        
    except ImportError:
        print_debug("LobbyHeader not available")
    except Exception as e:
        print_error("Failed to patch LobbyHeader: %s" % str(e))

def patch_messenger():
    try:
        from messenger.formatters import chat_message
        
        if not hasattr(chat_message, 'formatMessage'):
            print_debug("chat_message.formatMessage not found")
            return
        
        if hasattr(chat_message, '_original_formatMessage'):
            print_debug("chat_message.formatMessage already patched, skipping")
            return
        
        original_formatMessage = chat_message.formatMessage
        
        def patched_formatMessage(message, **kwargs):
            result = original_formatMessage(message, **kwargs)
            
            try:
                original_player_name = get_shared_data('original_name')
                if original_player_name and isinstance(result, dict):
                    new_name = get_shared_data('new_name')
                    
                    if result.get('userName') == original_player_name:
                        result['userName'] = new_name
                        print_debug("Chat: name changed in message")
                    
                    if 'message' in result and original_player_name in result['message']:
                        result['message'] = result['message'].replace(original_player_name, new_name)
            except Exception as e:
                print_error("Error in patched formatMessage: %s" % str(e))
            
            return result
        
        chat_message._original_formatMessage = original_formatMessage
        chat_message.formatMessage = patched_formatMessage
        print_debug("chat_message.formatMessage patched successfully")
        
    except ImportError:
        print_debug("Messenger chat_message not available")
    except Exception as e:
        print_error("Error patching messenger: %s" % str(e))
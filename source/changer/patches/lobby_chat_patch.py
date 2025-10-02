# -*- coding: utf-8 -*-
import BigWorld
from gui.Scaleform.daapi.view.lobby.header.LobbyHeader import LobbyHeader
from gui.shared.personality import ServicesLocator
from ..utils import print_debug, print_error

_original_getPlayerFullName = None
_original_setPlayerInfo = None
_original_player_name = None
_config = None

def patch(config):
    global _config, _original_getPlayerFullName, _original_setPlayerInfo
    _config = config
    
    print_debug("Starting lobby chat patches...")
    _get_original_player_name()
    
    try:
        _original_getPlayerFullName = ServicesLocator.lobbyContext.getPlayerFullName
        _original_setPlayerInfo = LobbyHeader._LobbyHeader__setPlayerInfo
        print_debug("Original lobby methods stored")
    except Exception as e:
        print_error("Error storing original lobby methods: %s" % str(e))
        return

    try:
        ServicesLocator.lobbyContext.getPlayerFullName = _patched_getPlayerFullName
        LobbyHeader._LobbyHeader__setPlayerInfo = _patched_setPlayerInfo
        print_debug("Lobby chat patched successfully")
    except Exception as e:
        print_error("Error patching lobby chat: %s" % str(e))
    
    patch_messenger()

def _get_original_player_name():
    global _original_player_name
    try:
        player = BigWorld.player()
        if player and hasattr(player, 'name') and player.name:
            _original_player_name = player.name
            print_debug("Lobby: Original player name set: %s" % _original_player_name)
        else:
            print_debug("Lobby: Player not ready, retrying...")
            BigWorld.callback(1.0, _get_original_player_name)
    except Exception as e:
        print_error("Error getting original player name: %s" % str(e))
        BigWorld.callback(1.0, _get_original_player_name)

def _patched_getPlayerFullName(pName, clanInfo=None, clanAbbrev=None, regionCode=None, pDBID=None):
    try:
        if _original_player_name and pName == _original_player_name:
            new_name = _config.load_nickname_from_config()
            print_debug("Lobby: getPlayerFullName changed '%s' -> '%s'" % (pName, new_name))
            
            if clanAbbrev:
                return '[%s] %s' % (clanAbbrev, new_name)
            return new_name
        
        return _original_getPlayerFullName(pName, clanInfo, clanAbbrev, regionCode, pDBID)
    except Exception as e:
        print_error("Error in getPlayerFullName: %s" % str(e))
        return _original_getPlayerFullName(pName, clanInfo, clanAbbrev, regionCode, pDBID)

def _patched_setPlayerInfo(instance, tooltip, tooltipType, tooltipArgs=None, warningIcon=False, userVO=None):
    try:
        if userVO and _original_player_name:
            if userVO.get('userName') == _original_player_name:
                new_name = _config.load_nickname_from_config()
                clanAbbrev = userVO.get('clanAbbrev', None)
                
                userVO['userName'] = new_name
                userVO['fullName'] = new_name if not clanAbbrev else '[%s] %s' % (clanAbbrev, new_name)
                
                print_debug("Lobby: setPlayerInfo changed name to '%s'" % new_name)
        
        return _original_setPlayerInfo(instance, tooltip, tooltipType, tooltipArgs, warningIcon, userVO)
    except Exception as e:
        print_error("Error in setPlayerInfo: %s" % str(e))
        return _original_setPlayerInfo(instance, tooltip, tooltipType, tooltipArgs, warningIcon, userVO)

def patch_messenger():
    try:
        from messenger.formatters import chat_message
        
        if hasattr(chat_message, 'formatMessage'):
            original_formatMessage = chat_message.formatMessage
            
            def patched_formatMessage(message, **kwargs):
                result = original_formatMessage(message, **kwargs)
                
                if _original_player_name and isinstance(result, dict):
                    if result.get('userName') == _original_player_name:
                        new_name = _config.load_nickname_from_config()
                        result['userName'] = new_name
                        print_debug("Messenger: Changed userName in message")

                    if 'message' in result and _original_player_name in result['message']:
                        new_name = _config.load_nickname_from_config()
                        result['message'] = result['message'].replace(_original_player_name, new_name)
                        print_debug("Messenger: Changed name in message text")
                
                return result
            
            chat_message.formatMessage = patched_formatMessage
            print_debug("Messenger formatMessage patched")
    except ImportError:
        print_debug("Messenger chat_message not available")
    except Exception as e:
        print_error("Error patching messenger: %s" % str(e))
    try:
        from messenger.formatters.users_messages import UserMessagesFormatter
        
        if hasattr(UserMessagesFormatter, 'format'):
            original_format = UserMessagesFormatter.format
            
            def patched_format(self, message, **kwargs):
                result = original_format(self, message, **kwargs)
                
                if _original_player_name and isinstance(result, dict):
                    if result.get('userName') == _original_player_name:
                        new_name = _config.load_nickname_from_config()
                        result['userName'] = new_name
                        print_debug("UserMessagesFormatter: Changed userName")
                
                return result
            
            UserMessagesFormatter.format = patched_format
            print_debug("UserMessagesFormatter patched")
    except ImportError:
        print_debug("UserMessagesFormatter not available")
    except Exception as e:
        print_error("Error patching UserMessagesFormatter: %s" % str(e))
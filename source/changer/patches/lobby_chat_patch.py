# -*- coding: utf-8 -*-
import BigWorld
from ..utils import print_debug, print_error, get_shared_data

def patch():
    
    print_debug("Starting lobby chat patches...")
    
    patch_lobby_context()
    patch_lobby_header()
    patch_lobby_message_builder()
    patch_battle_message_builder()
    
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


def patch_lobby_message_builder():
    try:
        from messenger.formatters.chat_message import LobbyMessageBuilder
        
        if hasattr(LobbyMessageBuilder, '_original_setName'):
            print_debug("LobbyMessageBuilder.setName already patched, skipping")
            return
        
        original_setName = LobbyMessageBuilder.setName
        
        def patched_setName(self, dbID, nickName, clanAbbrev=None):
            try:
                original_player_name = get_shared_data('original_name')
                myDBID = get_shared_data('accountDBID')
                
                if myDBID and dbID == myDBID and original_player_name and nickName == original_player_name:
                    new_name = get_shared_data('new_name')
                    print_debug("Lobby chat: name changed in LobbyMessageBuilder")
                    return original_setName(self, dbID, new_name, clanAbbrev)
                
                return original_setName(self, dbID, nickName, clanAbbrev)
            except Exception as e:
                print_error("Error in patched LobbyMessageBuilder.setName: %s" % str(e))
                return original_setName(self, dbID, nickName, clanAbbrev)
        
        LobbyMessageBuilder._original_setName = original_setName
        LobbyMessageBuilder.setName = patched_setName
        print_debug("LobbyMessageBuilder.setName patched successfully")
        
    except ImportError:
        print_debug("LobbyMessageBuilder not available")
    except Exception as e:
        print_error("Failed to patch LobbyMessageBuilder: %s" % str(e))


def patch_battle_message_builder():
    try:
        from messenger.formatters.chat_message import _BattleMessageBuilder
        
        if hasattr(_BattleMessageBuilder, '_original_setName'):
            print_debug("_BattleMessageBuilder.setName already patched, skipping")
            return
        
        original_setName = _BattleMessageBuilder.setName
        
        def patched_setName(self, avatarSessionID, pName=None, suffix=''):
            try:
                original_player_name = get_shared_data('original_name')
                
                if original_player_name and pName and pName == original_player_name:
                    new_name = get_shared_data('new_name')
                    print_debug("Battle chat: name changed in _BattleMessageBuilder")
                    return original_setName(self, avatarSessionID, new_name, suffix)
                
                return original_setName(self, avatarSessionID, pName, suffix)
            except Exception as e:
                print_error("Error in patched _BattleMessageBuilder.setName: %s" % str(e))
                return original_setName(self, avatarSessionID, pName, suffix)
        
        _BattleMessageBuilder._original_setName = original_setName
        _BattleMessageBuilder.setName = patched_setName
        print_debug("_BattleMessageBuilder.setName patched successfully")
        
    except ImportError:
        print_debug("_BattleMessageBuilder not available")
    except Exception as e:
        print_error("Failed to patch _BattleMessageBuilder: %s" % str(e))
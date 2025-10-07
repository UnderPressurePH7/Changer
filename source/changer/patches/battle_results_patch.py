# -*- coding: utf-8 -*-
import BigWorld
from account_helpers import getAccountDatabaseID
from ..utils import print_debug, print_error, get_shared_data

_config = None

def patch(config):
    global _config
    _config = config
    
    print_debug("Starting battle results patches...")
    
    patch_player_info()
    patch_personal_avatar_info()
    patch_components_common()
    patch_player_name_display()
    
    print_debug("All battle results patches applied")


def patch_player_info():
    try:
        from gui.battle_results.reusable.players import PlayerInfo
        print_debug("Patching PlayerInfo.__init__...")
        
        if hasattr(PlayerInfo, '_original_init'):
            print_debug("PlayerInfo.__init__ already patched, skipping")
            return
        
        original_init = PlayerInfo.__init__
        
        def patched_init(self, dbID=0, team=0, name='', realName='', prebattleID=0, igrType=0, clanAbbrev='', clanDBID=0, wasInBattle=True, **kwargs):
            original_init(self, dbID, team, name, realName, prebattleID, igrType, clanAbbrev, clanDBID, wasInBattle, **kwargs)
            
            try:
                myDBID = getAccountDatabaseID()
                if dbID == myDBID and myDBID is not None:
                    new_name = _config.load_nickname_from_config()
                    if new_name:
                        self._PlayerInfo__fakeName = new_name
                        self._PlayerInfo__realName = new_name
                        print_debug("PlayerInfo patched: Changed player name to '%s' for dbID %s" % (new_name, dbID))
            except Exception as e:
                print_error("Error in patched PlayerInfo.__init__: %s" % str(e))
        
        PlayerInfo._original_init = original_init
        PlayerInfo.__init__ = patched_init
        print_debug("PlayerInfo.__init__ patched successfully")
        
    except ImportError:
        print_debug("PlayerInfo not available")
    except Exception as e:
        print_error("Failed to patch PlayerInfo: %s" % str(e))


def patch_personal_avatar_info():
    try:
        from gui.battle_results.reusable.personal import PersonalAvatarInfo
        print_debug("Patching PersonalAvatarInfo.__init__...")
        
        if hasattr(PersonalAvatarInfo, '_original_init'):
            print_debug("PersonalAvatarInfo.__init__ already patched, skipping")
            return
        
        original_init = PersonalAvatarInfo.__init__
        
        def patched_init(self, bonusType, accountDBID=0, clanDBID=0, team=0, isPrematureLeave=False, fairplayViolations=None, squadBonusInfo=None, winnerIfDraw=0, eligibleForCrystalRewards=False, avatarPlayerSatisfactionRating=(), commendationsReceived=0, **kwargs):
            original_init(self, bonusType, accountDBID, clanDBID, team, isPrematureLeave, fairplayViolations, squadBonusInfo, winnerIfDraw, eligibleForCrystalRewards, avatarPlayerSatisfactionRating, commendationsReceived, **kwargs)
            
            try:
                myDBID = getAccountDatabaseID()
                if accountDBID == myDBID and myDBID is not None:
                    new_name = _config.load_nickname_from_config()
                    if new_name:
                        print_debug("PersonalAvatarInfo: Player DBID matched, nickname change applied")
            except Exception as e:
                print_error("Error in patched PersonalAvatarInfo.__init__: %s" % str(e))
        
        PersonalAvatarInfo._original_init = original_init
        PersonalAvatarInfo.__init__ = patched_init
        print_debug("PersonalAvatarInfo.__init__ patched successfully")
        
    except ImportError:
        print_debug("PersonalAvatarInfo not available")
    except Exception as e:
        print_error("Failed to patch PersonalAvatarInfo: %s" % str(e))


def patch_components_common():
    try:
        from gui.battle_results.components import style
        print_debug("Patching style components...")
        
        if hasattr(style, '_original_getPlayerName'):
            print_debug("style components already patched, skipping")
            return
        
        if hasattr(style, 'getPlayerName'):
            original_getPlayerName = style.getPlayerName
            
            def patched_getPlayerName(playerInfo, showClan=True, showRegion=False):
                try:
                    myDBID = getAccountDatabaseID()
                    if hasattr(playerInfo, 'dbID') and playerInfo.dbID == myDBID and myDBID is not None:
                        new_name = _config.load_nickname_from_config()
                        if new_name:
                            print_debug("style.getPlayerName: Changing display name to '%s'" % new_name)
                            from gui.battle_results.reusable.players import PlayerInfo
                            modified_player = PlayerInfo(
                                dbID=playerInfo.dbID,
                                team=playerInfo.team,
                                name=new_name,
                                realName=new_name,
                                prebattleID=playerInfo.prebattleID,
                                igrType=playerInfo.igrType,
                                clanAbbrev=playerInfo.clanAbbrev,
                                clanDBID=playerInfo.clanDBID
                            )
                            return original_getPlayerName(modified_player, showClan, showRegion)
                    
                    return original_getPlayerName(playerInfo, showClan, showRegion)
                except Exception as e:
                    print_error("Error in patched getPlayerName: %s" % str(e))
                    return original_getPlayerName(playerInfo, showClan, showRegion)
            
            style._original_getPlayerName = original_getPlayerName
            style.getPlayerName = patched_getPlayerName
            print_debug("style.getPlayerName patched successfully")
        
    except ImportError:
        print_debug("style components not available")
    except Exception as e:
        print_error("Failed to patch style components: %s" % str(e))


def patch_player_name_display():
    try:
        from gui.battle_results.reusable import players
        
        if hasattr(players.PlayerInfo, 'getFullName'):
            original_getFullName = players.PlayerInfo.getFullName
            
            def patched_getFullName(self):
                try:
                    myDBID = getAccountDatabaseID()
                    if self.dbID == myDBID and myDBID is not None:
                        new_name = _config.load_nickname_from_config()
                        if new_name:
                            from helpers import dependency
                            from skeletons.gui.lobby_context import ILobbyContext
                            lobbyContext = dependency.instance(ILobbyContext)
                            return lobbyContext.getPlayerFullName(new_name, clanAbbrev=self.clanAbbrev, pDBID=self.dbID)
                    
                    return original_getFullName(self)
                except Exception as e:
                    print_error("Error in patched getFullName: %s" % str(e))
                    return original_getFullName(self)
            
            players.PlayerInfo.getFullName = patched_getFullName
            print_debug("PlayerInfo.getFullName patched successfully")
        
    except Exception as e:
        print_error("Failed to patch player name display: %s" % str(e))
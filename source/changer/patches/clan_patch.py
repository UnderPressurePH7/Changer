# -*- coding: utf-8 -*-
import BigWorld
from account_helpers import getAccountDatabaseID
from ..utils import print_debug, print_error, get_shared_data

_config = None

def patch(config):
    global _config
    _config = config
    
    print_debug("Starting clan patches...")
    
    patch_clan_profile_personnel()
    patch_clan_profile_summary()
    
    print_debug("All clan patches applied")


def patch_clan_profile_personnel():
    try:
        from gui.Scaleform.daapi.view.lobby.clans.profile.ClanProfilePersonnelView import _ClanMembersDataProvider
        
        original_makeVO = _ClanMembersDataProvider._makeVO
        
        def patched_makeVO(self, memberData):
            vo = original_makeVO(self, memberData)
            
            try:
                memberDBID = memberData.getDbID()
                myDBID = getAccountDatabaseID()
                
                if memberDBID == myDBID:
                    new_name = _config.load_nickname_from_config()
                    vo['userName'] = new_name
                    
                    if 'contactItem' in vo and 'userProps' in vo['contactItem']:
                        vo['contactItem']['userProps']['userName'] = new_name
                    
                    print_debug("ClanProfilePersonnelView: Changed userName to '%s'" % new_name)
            except Exception as e:
                print_error("Error in patched _ClanMembersDataProvider._makeVO: %s" % str(e))
            
            return vo
        
        _ClanMembersDataProvider._makeVO = patched_makeVO
        print_debug("ClanProfilePersonnelView patched successfully")
        
    except ImportError:
        print_debug("ClanProfilePersonnelView not available")
    except Exception as e:
        print_error("Failed to patch ClanProfilePersonnelView: %s" % str(e))


def patch_clan_profile_summary():
    try:
        from gui.Scaleform.daapi.view.lobby.clans.profile.ClanProfileSummaryView import ClanProfileSummaryView
        
        original_makeGeneralBlock = ClanProfileSummaryView._ClanProfileSummaryView__makeGeneralBlock
        
        def patched_makeGeneralBlock(self, clanInfo, syncUserInfo=False):
            result = original_makeGeneralBlock(self, clanInfo, syncUserInfo)
            
            try:
                player = BigWorld.player()
                if player and hasattr(clanInfo, 'getLeaderDbID'):
                    leaderDBID = clanInfo.getLeaderDbID()
                    
                    if leaderDBID == player.databaseID:
                        new_name = _config.load_nickname_from_config()

                        if 'statBlocks' in result:
                            for stat in result['statBlocks']:
                                if stat.get('label') and 'commander' in stat.get('label', '').lower():
                                    import re
                                    style_match = re.search(r'<font[^>]*>(.*?)</font>', stat['value'])
                                    if style_match:
                                        stat['value'] = stat['value'].replace(style_match.group(1), new_name)
                                    else:
                                        stat['value'] = new_name
                                    
                                    print_debug("ClanProfileSummaryView: Changed commander name to '%s'" % new_name)
                                    break
            except Exception as e:
                print_error("Error in patched __makeGeneralBlock: %s" % str(e))
            
            return result
        
        ClanProfileSummaryView._ClanProfileSummaryView__makeGeneralBlock = patched_makeGeneralBlock
        print_debug("ClanProfileSummaryView patched successfully")
        
    except ImportError:
        print_debug("ClanProfileSummaryView not available")
    except Exception as e:
        print_error("Failed to patch ClanProfileSummaryView: %s" % str(e))
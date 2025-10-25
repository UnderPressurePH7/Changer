# -*- coding: utf-8 -*-
from ..utils import print_debug, print_error, get_shared_data

try:
    unicode
except NameError:
    unicode = str

def patch():
    print_debug("Starting clan patches...")
    
    patch_clan_helpers()
    patch_clan_info()
    
    print_debug("Clan patches applied")


def patch_clan_helpers():
    try:
        from gui.Scaleform.daapi.view.lobby.clans.clan_helpers import ClanHelpers
        
        if hasattr(ClanHelpers, '_original_getClanFullName'):
            print_debug("ClanHelpers already patched, skipping")
            return
        
        if hasattr(ClanHelpers, 'getClanFullName'):
            original_getClanFullName = ClanHelpers.getClanFullName
            
            @staticmethod
            def patched_getClanFullName(clanName, clanAbbrev=None, userName=None):
                try:
                    original_name = get_shared_data('original_name')
                    if original_name and userName and userName == original_name:
                        new_name = get_shared_data('new_name')
                        return original_getClanFullName(clanName, clanAbbrev, new_name)
                except Exception as e:
                    print_error("Error in patched getClanFullName: %s" % str(e))
                
                return original_getClanFullName(clanName, clanAbbrev, userName)
            
            ClanHelpers._original_getClanFullName = original_getClanFullName
            ClanHelpers.getClanFullName = patched_getClanFullName
            print_debug("ClanHelpers.getClanFullName patched successfully")
        
    except ImportError:
        print_debug("ClanHelpers not available")
    except Exception as e:
        print_error("Failed to patch ClanHelpers: %s" % str(e))


def patch_clan_info():
    try:
        from gui.clans.clan_helpers import ClanInfo
        
        if hasattr(ClanInfo, '_original_getFullUserName'):
            print_debug("ClanInfo already patched, skipping")
            return
        
        if hasattr(ClanInfo, 'getFullUserName'):
            original_getFullUserName = ClanInfo.getFullUserName
            
            def patched_getFullUserName(self):
                result = original_getFullUserName(self)
                
                try:
                    original_name = get_shared_data('original_name')
                    new_name = get_shared_data('new_name')
                    
                    if original_name and new_name and isinstance(result, (str, unicode)):
                        if original_name in result:
                            result = result.replace(original_name, new_name)
                            print_debug("Clan: name changed in ClanInfo")
                except Exception as e:
                    print_error("Error in patched getFullUserName: %s" % str(e))
                
                return result
            
            ClanInfo._original_getFullUserName = original_getFullUserName
            ClanInfo.getFullUserName = patched_getFullUserName
            print_debug("ClanInfo.getFullUserName patched successfully")
        
    except ImportError:
        print_debug("ClanInfo not available")
    except Exception as e:
        print_error("Failed to patch ClanInfo: %s" % str(e))
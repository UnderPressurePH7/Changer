# -*- coding: utf-8 -*-
from ..utils import print_debug, print_error, get_shared_data

try:
    unicode
except NameError:
    unicode = str

def patch():
    
    print_debug("Starting clan patches...")
    
    patch_clan_formatters()
    patch_clan_emblem()
    
    print_debug("Clan patches applied")


def patch_clan_formatters():
    try:
        from gui.shared.formatters import text_styles
        
        try:
            from helpers import getPlayerNameWithClanAbbrev
            
            if not hasattr(getPlayerNameWithClanAbbrev, '__call__'):
                print_debug("getPlayerNameWithClanAbbrev is not callable")
            else:
                print_debug("getPlayerNameWithClanAbbrev found but it's a function (cannot patch)")
        except ImportError:
            print_debug("getPlayerNameWithClanAbbrev not available")
        try:
            from gui.shared.formatters.user_messages import makeFullPlayerName
            
            if hasattr(makeFullPlayerName, '__call__'):
                print_debug("makeFullPlayerName found but it's a function")
        except ImportError:
            print_debug("makeFullPlayerName not available")
        
        print_debug("Clan formatters checked (most are functions, patched via other means)")
        
    except Exception as e:
        print_error("Error in patch_clan_formatters: %s" % str(e))


def patch_clan_emblem():
    try:
        from gui.Scaleform.daapi.view.lobby.clans.clan_helpers import ClanHelpers
        
        if not hasattr(ClanHelpers, 'getPlayerClanEmblemID'):
            print_debug("ClanHelpers.getPlayerClanEmblemID not found")
            return
        
        print_debug("ClanHelpers found, checking methods...")
        
        if hasattr(ClanHelpers, 'getClanFullName'):
            if hasattr(ClanHelpers.getClanFullName, '__call__'):
                if hasattr(ClanHelpers, '_original_getClanFullName'):
                    print_debug("ClanHelpers.getClanFullName already patched, skipping")
                else:
                    original_getClanFullName = ClanHelpers.getClanFullName
                    
                    @staticmethod
                    def patched_getClanFullName(clanName, clanAbbrev=None, userName=None):
                        try:
                            original_name = get_shared_data('original_name')
                            if original_name and userName and userName == original_name:
                                new_name = get_shared_data('new_name')
                                result = original_getClanFullName(clanName, clanAbbrev, new_name)
                                print_debug("Clan: name changed in getClanFullName")
                                return result
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
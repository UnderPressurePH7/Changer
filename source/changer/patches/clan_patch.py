# -*- coding: utf-8 -*-
import BigWorld
from account_helpers import getAccountDatabaseID
from ..utils import print_debug, print_error, get_shared_data

_config = None

def patch(config):
    global _config
    _config = config
    
    print_debug("Starting clan patches...")
    
    patch_format_field()
    patch_clan_profile_personnel_direct()
    patch_clan_profile_summary()
    
    print_debug("All clan patches applied")


def patch_format_field():
    try:
        from gui.clans.data_wrapper.utils import formatField
        from gui.shared.view_helpers.UsersInfoHelper import UsersInfoHelper
        
        helper = UsersInfoHelper()
        original_formatField = formatField
        
        def patched_formatField(getter, formatter=None):
            result = original_formatField(getter, formatter)
            
            try:
                if formatter and hasattr(formatter, '__self__'):
                    if isinstance(result, (str, unicode)):
                        original_name = get_shared_data('original_name')
                        if original_name and result == original_name:
                            new_name = _config.load_nickname_from_config()
                            print_debug("formatField: Changed '%s' -> '%s'" % (result, new_name))
                            return new_name
            except Exception as e:
                print_error("Error in patched formatField: %s" % str(e))
            
            return result
        
        import gui.clans.data_wrapper.utils as utils_module
        utils_module.formatField = patched_formatField
        print_debug("formatField patched successfully")
        
    except ImportError:
        print_debug("formatField not available")
    except Exception as e:
        print_error("Failed to patch formatField: %s" % str(e))


def patch_clan_profile_personnel_direct():
    try:
        from gui.Scaleform.daapi.view.lobby.clans.profile.ClanProfilePersonnelView import _ClanMembersDataProvider
        
        original_getMemberName = _ClanMembersDataProvider._ClanMembersDataProvider__getMemberName
        
        def patched_getMemberName(self, memberData):
            name = original_getMemberName(self, memberData)
            
            try:
                memberDBID = memberData.getDbID()
                myDBID = getAccountDatabaseID()
                
                if memberDBID == myDBID:
                    original_name = get_shared_data('original_name')
                    if original_name and name == original_name:
                        new_name = _config.load_nickname_from_config()
                        print_debug("Personnel.__getMemberName: Changed '%s' -> '%s'" % (name, new_name))
                        return new_name
            except Exception as e:
                print_error("Error in patched __getMemberName: %s" % str(e))
            
            return name
        
        _ClanMembersDataProvider._ClanMembersDataProvider__getMemberName = patched_getMemberName
        print_debug("Personnel.__getMemberName patched successfully")
        
    except ImportError:
        print_debug("_ClanMembersDataProvider not available")
    except Exception as e:
        print_error("Failed to patch _ClanMembersDataProvider: %s" % str(e))


def patch_clan_profile_summary():
    try:
        from gui.Scaleform.daapi.view.lobby.clans.profile.ClanProfileSummaryView import ClanProfileSummaryView
        from gui.shared.view_helpers.UsersInfoHelper import UsersInfoHelper
        
        original_getGuiUserName = UsersInfoHelper.getGuiUserName
        
        def patched_getGuiUserName(self, userID, formatter=lambda v: v, scope=None):
            from messenger.m_constants import UserEntityScope
            if scope is None:
                scope = UserEntityScope.LOBBY
            
            name = original_getGuiUserName(self, userID, formatter, scope)
            
            try:
                myDBID = getAccountDatabaseID()
                if userID == myDBID and name:
                    original_name = get_shared_data('original_name')
                    if original_name and name == original_name:
                        new_name = _config.load_nickname_from_config()
                        print_debug("Summary.getGuiUserName: Changed '%s' -> '%s'" % (name, new_name))
                        return new_name
            except Exception as e:
                print_error("Error in patched getGuiUserName: %s" % str(e))
            
            return name
        
        UsersInfoHelper.getGuiUserName = patched_getGuiUserName
        print_debug("UsersInfoHelper.getGuiUserName patched successfully")
        
    except ImportError:
        print_debug("ClanProfileSummaryView not available")
    except Exception as e:
        print_error("Failed to patch ClanProfileSummaryView: %s" % str(e))
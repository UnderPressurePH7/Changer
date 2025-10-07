# -*- coding: utf-8 -*-
import BigWorld
from account_helpers import getAccountDatabaseID
from ..utils import print_debug, print_error, get_shared_data

_config = None

def patch(config):
    global _config
    _config = config
    
    print_debug("Starting clan patches...")
    
    patch_users_info_helper()
    patch_clan_profile_personnel_direct()
    
    print_debug("All clan patches applied")


def patch_users_info_helper():
    try:
        from gui.shared.view_helpers.UsersInfoHelper import UsersInfoHelper
        print_debug("Patching UsersInfoHelper.getUserName and getGuiUserName...")
        if hasattr(UsersInfoHelper, '_original_getUserName'):
            print_debug("UsersInfoHelper already patched, skipping")
            return
        
        original_getUserName = UsersInfoHelper.getUserName
        original_getGuiUserName = UsersInfoHelper.getGuiUserName
        
        def patched_getUserName(self, userID, scope=None):
            from messenger.m_constants import UserEntityScope
            if scope is None:
                scope = UserEntityScope.LOBBY
            
            name = original_getUserName(self, userID, scope)
            
            try:
                myDBID = getAccountDatabaseID()
                if userID == myDBID and name:
                    original_name = get_shared_data('original_name')
                    if original_name and name == original_name:
                        new_name = _config.load_nickname_from_config()
                        print_debug("UsersInfoHelper.getUserName: Changed '%s' -> '%s'" % (name, new_name))
                        return new_name
            except Exception as e:
                print_error("Error in patched getUserName: %s" % str(e))
            
            return name
        
        def patched_getGuiUserName(self, userID, formatter=lambda v: v, scope=None):
            from messenger.m_constants import UserEntityScope
            if scope is None:
                scope = UserEntityScope.LOBBY
            
            name = original_getGuiUserName(self, userID, formatter, scope)
            
            try:
                myDBID = getAccountDatabaseID()
                if userID == myDBID and name:
                    original_name = get_shared_data('original_name')
                    if original_name:
                        formatted_original = formatter(original_name)
                        if name == formatted_original:
                            new_name = _config.load_nickname_from_config()
                            formatted_new = formatter(new_name)
                            print_debug("UsersInfoHelper.getGuiUserName: Changed '%s' -> '%s'" % (name, formatted_new))
                            return formatted_new
            except Exception as e:
                print_error("Error in patched getGuiUserName: %s" % str(e))
            
            return name
        
        UsersInfoHelper._original_getUserName = original_getUserName
        UsersInfoHelper._original_getGuiUserName = original_getGuiUserName
        UsersInfoHelper.getUserName = patched_getUserName
        UsersInfoHelper.getGuiUserName = patched_getGuiUserName
        print_debug("UsersInfoHelper patched successfully")
        
    except ImportError:
        print_debug("UsersInfoHelper not available")
    except Exception as e:
        print_error("Failed to patch UsersInfoHelper: %s" % str(e))


def patch_clan_profile_personnel_direct():
    try:
        from gui.Scaleform.daapi.view.lobby.clans.profile.ClanProfilePersonnelView import _ClanMembersDataProvider
        
        mangled_name = '_ClanMembersDataProvider__getMemberName'
        
        if not hasattr(_ClanMembersDataProvider, mangled_name):
            print_debug("_ClanMembersDataProvider.__getMemberName not found")
            return
        
        if hasattr(_ClanMembersDataProvider, '_original__getMemberName'):
            print_debug("_ClanMembersDataProvider.__getMemberName already patched, skipping")
            return
        
        original_getMemberName = getattr(_ClanMembersDataProvider, mangled_name)
        
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
        
        setattr(_ClanMembersDataProvider, '_original__getMemberName', original_getMemberName)
        setattr(_ClanMembersDataProvider, mangled_name, patched_getMemberName)
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
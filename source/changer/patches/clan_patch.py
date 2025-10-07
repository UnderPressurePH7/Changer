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
    patch_clan_members_data_provider()
    patch_clan_profile_personnel()
    patch_clan_profile_summary()
    
    print_debug("All clan patches applied")


def patch_users_info_helper():
    try:
        from gui.shared.view_helpers.UsersInfoHelper import UsersInfoHelper
        print_debug("Patching UsersInfoHelper methods...")
        
        if hasattr(UsersInfoHelper, '_original_getUserName'):
            print_debug("UsersInfoHelper already patched, skipping")
            return
        
        original_getUserName = UsersInfoHelper.getUserName
        original_getGuiUserName = UsersInfoHelper.getGuiUserName
        
        def patched_getUserName(self, userID, scope=None):
            """Патч для getUserName - повертає кастомне ім'я для поточного гравця"""
            from messenger.m_constants import UserEntityScope
            if scope is None:
                scope = UserEntityScope.LOBBY
            
            try:
                myDBID = getAccountDatabaseID()
                if userID == myDBID and myDBID is not None:
                    new_name = _config.load_nickname_from_config()
                    if new_name:
                        print_debug("UsersInfoHelper.getUserName: Changed name to '%s' for userID %s" % (new_name, userID))
                        return new_name
            except Exception as e:
                print_error("Error in patched getUserName: %s" % str(e))
            
            return original_getUserName(self, userID, scope)
        
        def patched_getGuiUserName(self, userID, formatter=lambda v: v, scope=None):
            from messenger.m_constants import UserEntityScope
            if scope is None:
                scope = UserEntityScope.LOBBY
            
            try:
                myDBID = getAccountDatabaseID()
                if userID == myDBID and myDBID is not None:
                    new_name = _config.load_nickname_from_config()
                    if new_name:
                        formatted_name = formatter(new_name)
                        print_debug("UsersInfoHelper.getGuiUserName: Changed name to '%s' for userID %s" % (formatted_name, userID))
                        return formatted_name
            except Exception as e:
                print_error("Error in patched getGuiUserName: %s" % str(e))
            
            return original_getGuiUserName(self, userID, formatter, scope)
        
        UsersInfoHelper._original_getUserName = original_getUserName
        UsersInfoHelper._original_getGuiUserName = original_getGuiUserName
        UsersInfoHelper.getUserName = patched_getUserName
        UsersInfoHelper.getGuiUserName = patched_getGuiUserName
        
        print_debug("UsersInfoHelper methods patched successfully")
        
    except ImportError as e:
        print_debug("UsersInfoHelper not available: %s" % str(e))
    except Exception as e:
        print_error("Failed to patch UsersInfoHelper: %s" % str(e))


def patch_clan_members_data_provider():
    try:
        from gui.Scaleform.daapi.view.lobby.clans.profile.ClanProfilePersonnelView import _ClanMembersDataProvider
        print_debug("Patching _ClanMembersDataProvider...")
        
        mangled_name = '_ClanMembersDataProvider__getMemberName'
        
        if not hasattr(_ClanMembersDataProvider, mangled_name):
            print_debug("_ClanMembersDataProvider.__getMemberName not found, searching alternatives...")
            found = False
            for attr_name in dir(_ClanMembersDataProvider):
                if 'getMemberName' in attr_name:
                    print_debug("Found alternative method: %s" % attr_name)
                    mangled_name = attr_name
                    found = True
                    break
            
            if not found:
                print_debug("No getMemberName method found in _ClanMembersDataProvider")
                return
        
        if hasattr(_ClanMembersDataProvider, '_original__getMemberName'):
            print_debug("_ClanMembersDataProvider.__getMemberName already patched, skipping")
            return
        
        original_getMemberName = getattr(_ClanMembersDataProvider, mangled_name)
        
        def patched_getMemberName(self, memberData):
            try:
                memberDBID = memberData.getDbID()
                myDBID = getAccountDatabaseID()
                
                if memberDBID == myDBID and myDBID is not None:
                    new_name = _config.load_nickname_from_config()
                    if new_name:
                        print_debug("_ClanMembersDataProvider.__getMemberName: Changed name to '%s'" % new_name)
                        return new_name
            except Exception as e:
                print_error("Error in patched __getMemberName: %s" % str(e))
            
            return original_getMemberName(self, memberData)
        
        setattr(_ClanMembersDataProvider, '_original__getMemberName', original_getMemberName)
        setattr(_ClanMembersDataProvider, mangled_name, patched_getMemberName)
        print_debug("_ClanMembersDataProvider.__getMemberName patched successfully")
        
        if hasattr(_ClanMembersDataProvider, '_makeVO'):
            if not hasattr(_ClanMembersDataProvider, '_original_makeVO'):
                original_makeVO = _ClanMembersDataProvider._makeVO
                
                def patched_makeVO(self, memberData):
                    vo = original_makeVO(self, memberData)
                    
                    try:
                        memberDBID = memberData.getDbID()
                        myDBID = getAccountDatabaseID()
                        
                        if memberDBID == myDBID and myDBID is not None and isinstance(vo, dict):
                            new_name = _config.load_nickname_from_config()
                            if new_name:
                                if 'userName' in vo:
                                    vo['userName'] = new_name
                                
                                if 'contactItem' in vo and isinstance(vo['contactItem'], dict):
                                    if 'userProps' in vo['contactItem'] and isinstance(vo['contactItem']['userProps'], dict):
                                        vo['contactItem']['userProps']['userName'] = new_name
                                
                                print_debug("_ClanMembersDataProvider._makeVO: Updated userName to '%s'" % new_name)
                    except Exception as e:
                        print_error("Error in patched _makeVO: %s" % str(e))
                    
                    return vo
                
                _ClanMembersDataProvider._original_makeVO = original_makeVO
                _ClanMembersDataProvider._makeVO = patched_makeVO
                print_debug("_ClanMembersDataProvider._makeVO patched successfully")
        
    except ImportError as e:
        print_debug("_ClanMembersDataProvider not available: %s" % str(e))
    except Exception as e:
        print_error("Failed to patch _ClanMembersDataProvider: %s" % str(e))


def patch_clan_profile_personnel():
    try:
        from gui.Scaleform.daapi.view.lobby.clans.profile.ClanProfilePersonnelView import ClanProfilePersonnelView
        print_debug("Patching ClanProfilePersonnelView...")
        
        if hasattr(ClanProfilePersonnelView, '_original_setClanDossier'):
            print_debug("ClanProfilePersonnelView already patched, skipping")
            return
        
        original_setClanDossier = ClanProfilePersonnelView.setClanDossier
        
        def patched_setClanDossier(self, clanDossier):
            print_debug("ClanProfilePersonnelView.setClanDossier called")
            try:
                result = original_setClanDossier(self, clanDossier)
                
                if hasattr(self, '_ClanProfilePersonnelView__membersDP') and self._ClanProfilePersonnelView__membersDP:
                    print_debug("Refreshing clan members display after dossier update")
                    BigWorld.callback(0.1, lambda: self._ClanProfilePersonnelView__membersDP.refresh())
                
                return result
            except Exception as e:
                print_error("Error in patched setClanDossier: %s" % str(e))
                return original_setClanDossier(self, clanDossier)
        
        ClanProfilePersonnelView._original_setClanDossier = original_setClanDossier
        ClanProfilePersonnelView.setClanDossier = patched_setClanDossier
        
        print_debug("ClanProfilePersonnelView patched successfully")
        
    except ImportError as e:
        print_debug("ClanProfilePersonnelView not available: %s" % str(e))
    except Exception as e:
        print_error("Failed to patch ClanProfilePersonnelView: %s" % str(e))


def patch_clan_profile_summary():
    try:
        from gui.Scaleform.daapi.view.lobby.clans.profile.ClanProfileSummaryView import ClanProfileSummaryView
        print_debug("Patching ClanProfileSummaryView...")
        
        if hasattr(ClanProfileSummaryView, '_original_setClanDossier'):
            print_debug("ClanProfileSummaryView already patched, skipping")
            return
        
        original_setClanDossier = ClanProfileSummaryView.setClanDossier
        
        def patched_setClanDossier(self, clanDossier):
            print_debug("ClanProfileSummaryView.setClanDossier called")
            try:
                result = original_setClanDossier(self, clanDossier)
                
                myDBID = getAccountDatabaseID()
                if myDBID and clanDossier:
                    new_name = _config.load_nickname_from_config()
                    print_debug("ClanProfileSummaryView: Using custom name '%s' for summary" % new_name)
                
                return result
            except Exception as e:
                print_error("Error in patched ClanProfileSummaryView.setClanDossier: %s" % str(e))
                return original_setClanDossier(self, clanDossier)
        
        ClanProfileSummaryView._original_setClanDossier = original_setClanDossier  
        ClanProfileSummaryView.setClanDossier = patched_setClanDossier
        
        print_debug("ClanProfileSummaryView patched successfully")
        
    except ImportError as e:
        print_debug("ClanProfileSummaryView not available: %s" % str(e))
    except Exception as e:
        print_error("Failed to patch ClanProfileSummaryView: %s" % str(e))

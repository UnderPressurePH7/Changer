# -*- coding: utf-8 -*-
import BigWorld
from account_helpers import getAccountDatabaseID
from ..utils import print_debug, print_error, get_shared_data

try:
    unicode
except NameError:
    unicode = str

def patch():
    
    print_debug("Starting stats patches...")
    
    patch_profile_formatters()
    patch_dossier_display()
    patch_user_string()
    
    print_debug("Stats patches applied")


def patch_profile_formatters():
    try:
        from gui.shared.formatters import text_styles
        from gui.Scaleform.daapi.view.lobby.profile.ProfileUtils import ProfileUtils
        
        if not hasattr(ProfileUtils, 'packProfileDossierInfo'):
            print_debug("ProfileUtils.packProfileDossierInfo not found")
            return
        
        if hasattr(ProfileUtils, '_original_packProfileDossierInfo'):
            print_debug("ProfileUtils already patched, skipping")
            return
        
        original_packProfileDossierInfo = ProfileUtils.packProfileDossierInfo
        
        @staticmethod
        def patched_packProfileDossierInfo(databaseID, *args, **kwargs):
            result = original_packProfileDossierInfo(databaseID, *args, **kwargs)
            
            try:
                myDBID = getAccountDatabaseID()
                if myDBID and databaseID == myDBID:
                    original_name = get_shared_data('original_name')
                    if original_name and isinstance(result, dict):
                        new_name = get_shared_data('new_name')
                        
                        for key in ('userName', 'name', 'fullUserName'):
                            if key in result and isinstance(result[key], (str, unicode)):
                                if original_name in result[key]:
                                    result[key] = result[key].replace(original_name, new_name)
                                    print_debug("Profile: name changed in %s" % key)
            
            except Exception as e:
                print_error("Error in patched packProfileDossierInfo: %s" % str(e))
            
            return result
        
        ProfileUtils._original_packProfileDossierInfo = original_packProfileDossierInfo
        ProfileUtils.packProfileDossierInfo = patched_packProfileDossierInfo
        print_debug("ProfileUtils.packProfileDossierInfo patched successfully")
        
    except ImportError:
        print_debug("ProfileUtils not available")
    except Exception as e:
        print_error("Failed to patch ProfileUtils: %s" % str(e))


def patch_dossier_display():
    try:
        from gui.shared.gui_items.dossier.dossier import AccountDossier
        
        if not hasattr(AccountDossier, 'getUserName'):
            print_debug("AccountDossier.getUserName not found")
            return
        
        if hasattr(AccountDossier, '_original_getUserName'):
            print_debug("AccountDossier already patched, skipping")
            return
        
        original_getUserName = AccountDossier.getUserName
        
        def patched_getUserName(self):
            original_name = original_getUserName(self)
            
            try:
                myDBID = getAccountDatabaseID()
                if not myDBID:
                    return original_name
                
                if hasattr(self, '_databaseID') and self._databaseID == myDBID:
                    stored_original = get_shared_data('original_name')
                    if stored_original and original_name == stored_original:
                        new_name = get_shared_data('new_name')
                        print_debug("Dossier: name changed in getUserName")
                        return new_name
            
            except Exception as e:
                print_error("Error in patched getUserName: %s" % str(e))
            
            return original_name
        
        AccountDossier._original_getUserName = original_getUserName
        AccountDossier.getUserName = patched_getUserName
        print_debug("AccountDossier.getUserName patched successfully")
        
    except ImportError:
        print_debug("AccountDossier not available")
    except Exception as e:
        print_error("Failed to patch AccountDossier: %s" % str(e))


def patch_user_string():
    try:
        from gui.shared.utils.requesters import StatsRequester
        
        if not hasattr(StatsRequester, 'getUserName'):
            print_debug("StatsRequester.getUserName not found")
            return
        
        if hasattr(StatsRequester, '_original_getUserName'):
            print_debug("StatsRequester already patched, skipping")
            return
        
        original_getUserName = StatsRequester.getUserName
        
        def patched_getUserName(self):
            """Патчить отримання імені зі StatsRequester"""
            original_name = original_getUserName(self)
            
            try:
                myDBID = getAccountDatabaseID()
                if not myDBID:
                    return original_name
                
                if hasattr(self, 'databaseID') and self.databaseID == myDBID:
                    stored_original = get_shared_data('original_name')
                    if stored_original and original_name == stored_original:
                        new_name = get_shared_data('new_name')
                        print_debug("Stats: name changed in StatsRequester")
                        return new_name
            
            except Exception as e:
                print_error("Error in patched StatsRequester.getUserName: %s" % str(e))
            
            return original_name
        
        StatsRequester._original_getUserName = original_getUserName
        StatsRequester.getUserName = patched_getUserName
        print_debug("StatsRequester.getUserName patched successfully")
        
    except ImportError:
        print_debug("StatsRequester not available")
    except Exception as e:
        print_error("Failed to patch StatsRequester: %s" % str(e))
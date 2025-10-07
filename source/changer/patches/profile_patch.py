# -*- coding: utf-8 -*-
import BigWorld
from account_helpers import getAccountDatabaseID
from ..utils import print_debug, print_error, get_shared_data

_config = None

def patch(config):
    global _config
    _config = config
    
    print_debug("Starting profile patches...")
    
    patch_profile_page()
    patch_profile_window()
    patch_profile_utils()
    patch_profile_data_builders()
    
    print_debug("All profile patches applied")


def patch_profile_page():
    try:
        from gui.Scaleform.daapi.view.lobby.profile.ProfilePage import ProfilePage
        print_debug("Patching ProfilePage._populate...")
        
        if hasattr(ProfilePage, '_original_populate'):
            print_debug("ProfilePage already patched, skipping")
            return
        
        original_populate = ProfilePage._populate
        
        def patched_populate(self):
            try:
                player = BigWorld.player()
                myDBID = getAccountDatabaseID()
                
                if player and hasattr(player, 'databaseID') and player.databaseID == myDBID:
                    new_name = _config.load_nickname_from_config()
                    if new_name and hasattr(player, 'name'):
                        original_name = player.name
                        player.name = new_name
                        print_debug("ProfilePage: Temporarily changed player name to '%s'" % new_name)
                        
                        try:
                            original_populate(self)
                        finally:
                            player.name = original_name
                        return
                
                original_populate(self)
                
            except Exception as e:
                print_error("Error in patched ProfilePage._populate: %s" % str(e))
                original_populate(self)
        
        ProfilePage._original_populate = original_populate
        ProfilePage._populate = patched_populate
        print_debug("ProfilePage._populate patched successfully")
        
    except ImportError as e:
        print_debug("ProfilePage not available: %s" % str(e))
    except Exception as e:
        print_error("Failed to patch ProfilePage: %s" % str(e))


def patch_profile_window():
    try:
        from gui.Scaleform.daapi.view.lobby.profile.ProfileWindow import ProfileWindow
        print_debug("Patching ProfileWindow._populate...")
        
        if hasattr(ProfileWindow, '_original_populate'):
            print_debug("ProfileWindow already patched, skipping")
            return
        
        original_populate = ProfileWindow._populate
        
        def patched_populate(self):
            try:
                myDBID = getAccountDatabaseID()
                if hasattr(self, '_ProfileWindow__databaseID') and self._ProfileWindow__databaseID == myDBID:
                    new_name = _config.load_nickname_from_config()
                    if new_name:
                        print_debug("ProfileWindow: Viewing own profile, using custom name '%s'" % new_name)
                        
                        if hasattr(self, '_ProfileWindow__userName'):
                            original_userName = self._ProfileWindow__userName
                            self._ProfileWindow__userName = new_name
                            
                            try:
                                original_populate(self)
                            finally:
                                self._ProfileWindow__userName = original_userName
                            return
                
                original_populate(self)
                
            except Exception as e:
                print_error("Error in patched ProfileWindow._populate: %s" % str(e))
                original_populate(self)
        
        ProfileWindow._original_populate = original_populate
        ProfileWindow._populate = patched_populate
        
        if hasattr(ProfileWindow, '_ProfileWindow__updateUserInfo'):
            original_updateUserInfo = ProfileWindow._ProfileWindow__updateUserInfo
            
            def patched_updateUserInfo(self):
                try:
                    myDBID = getAccountDatabaseID()
                    
                    if hasattr(self, '_ProfileWindow__databaseID') and self._ProfileWindow__databaseID == myDBID:
                        new_name = _config.load_nickname_from_config()
                        if new_name and hasattr(self, '_ProfileWindow__userName'):
                            original_userName = self._ProfileWindow__userName
                            self._ProfileWindow__userName = new_name
                            
                            try:
                                original_updateUserInfo(self)
                            finally:
                                self._ProfileWindow__userName = original_userName
                            return
                    
                    original_updateUserInfo(self)
                    
                except Exception as e:
                    print_error("Error in patched ProfileWindow.__updateUserInfo: %s" % str(e))
                    original_updateUserInfo(self)
            
            ProfileWindow._original_updateUserInfo = original_updateUserInfo
            ProfileWindow._ProfileWindow__updateUserInfo = patched_updateUserInfo
            print_debug("ProfileWindow.__updateUserInfo patched successfully")
        
        print_debug("ProfileWindow patched successfully")
        
    except ImportError as e:
        print_debug("ProfileWindow not available: %s" % str(e))
    except Exception as e:
        print_error("Failed to patch ProfileWindow: %s" % str(e))


def patch_profile_utils():
    try:
        from gui.Scaleform.daapi.view.lobby.profile import ProfileUtils
        print_debug("Patching ProfileUtils.getProfileCommonInfo...")
        
        if not hasattr(ProfileUtils, 'getProfileCommonInfo'):
            print_debug("ProfileUtils.getProfileCommonInfo not found")
            return
        
        if hasattr(ProfileUtils.getProfileCommonInfo, '_original_function'):
            print_debug("getProfileCommonInfo already patched, skipping")
            return
        
        original_getProfileCommonInfo = ProfileUtils.getProfileCommonInfo
        
        def patched_getProfileCommonInfo(userName, dossierDescr):
            try:

                info = original_getProfileCommonInfo(userName, dossierDescr)
                
                # Перевіряємо чи це наш профіль за іменем
                original_player_name = get_shared_data('original_name')
                myDBID = getAccountDatabaseID()
                
                if original_player_name and userName == original_player_name and myDBID is not None:
                    new_name = _config.load_nickname_from_config()
                    if new_name and isinstance(info, dict) and 'name' in info:
                        info['name'] = new_name
                        print_debug("ProfileUtils.getProfileCommonInfo: Changed name to '%s'" % new_name)
                
                return info
                
            except Exception as e:
                print_error("Error in patched getProfileCommonInfo: %s" % str(e))
                return original_getProfileCommonInfo(userName, dossierDescr)

        patched_getProfileCommonInfo._original_function = original_getProfileCommonInfo
        ProfileUtils.getProfileCommonInfo = patched_getProfileCommonInfo
        
        print_debug("ProfileUtils.getProfileCommonInfo patched successfully")
        
    except ImportError as e:
        print_debug("ProfileUtils not available: %s" % str(e))
    except Exception as e:
        print_error("Failed to patch ProfileUtils: %s" % str(e))


def patch_profile_data_builders():
    try:
        from gui.Scaleform.daapi.view.lobby.profile import profile_helper
        print_debug("Patching profile data builders...")
        
        if hasattr(profile_helper, 'getPlayerName'):
            original_getPlayerName = profile_helper.getPlayerName
            
            def patched_getPlayerName(userName, clanAbbrev='', regionCode=''):
                try:
                    original_player_name = get_shared_data('original_name')
                    
                    if original_player_name and userName == original_player_name:
                        new_name = _config.load_nickname_from_config()
                        if new_name:
                            print_debug("profile_helper.getPlayerName: Using custom name '%s'" % new_name)
                            return original_getPlayerName(new_name, clanAbbrev, regionCode)
                    
                    return original_getPlayerName(userName, clanAbbrev, regionCode)
                    
                except Exception as e:
                    print_error("Error in patched getPlayerName: %s" % str(e))
                    return original_getPlayerName(userName, clanAbbrev, regionCode)
            
            profile_helper.getPlayerName = patched_getPlayerName
            print_debug("profile_helper.getPlayerName patched successfully")
        
    except ImportError as e:
        print_debug("profile_helper not available: %s" % str(e))
    except Exception as e:
        print_error("Failed to patch profile data builders: %s" % str(e))


def patch_profile_technique():
    try:
        from gui.Scaleform.daapi.view.lobby.profile.ProfileTechnique import ProfileTechnique
        print_debug("Checking ProfileTechnique...")
        
        if hasattr(ProfileTechnique, '_populate'):
            original_populate = ProfileTechnique._populate
            
            def patched_populate(self):
                try:
                    myDBID = getAccountDatabaseID()
                    
                    if hasattr(self, '_ProfileTechnique__databaseID') and self._ProfileTechnique__databaseID == myDBID:
                        new_name = _config.load_nickname_from_config()
                        if new_name:
                            print_debug("ProfileTechnique: Using custom name for own technique")
                            
                            player = BigWorld.player()
                            if player and hasattr(player, 'name'):
                                original_name = player.name
                                player.name = new_name
                                
                                try:
                                    original_populate(self)
                                finally:
                                    player.name = original_name
                                return
                    
                    original_populate(self)
                    
                except Exception as e:
                    print_error("Error in patched ProfileTechnique._populate: %s" % str(e))
                    original_populate(self)
            
            ProfileTechnique._populate = patched_populate
            print_debug("ProfileTechnique._populate patched successfully")
        
    except ImportError as e:
        print_debug("ProfileTechnique not available: %s" % str(e))
    except Exception as e:
        print_error("Failed to patch ProfileTechnique: %s" % str(e))
# -*- coding: utf-8 -*-
import BigWorld
from ..utils import print_debug, print_error, get_shared_data

try:
    unicode
except NameError:
    unicode = str

_config = None

def patch():

    print_debug("Starting models patches...")
    
    patch_account_model()
    patch_user_name_model()
    
    print_debug("All models patches applied")


def patch_account_model():
    global _original_AccountModel_setUserName
    try:
        from gui.impl.gen.view_models.common.account_model import AccountModel
        
        original_getUserName = AccountModel.getUserName
        
        def patched_getUserName(self):
            try:
                original_name = original_getUserName(self)
                
                myDBID = getAccountDatabaseID()
                if myDBID is None:
                    print_debug("Account DBID is None, returning original name")
                    return original_name
                
                model_dbid = self.getDatabaseID()
                
                if model_dbid == myDBID:
                    stored_original = get_shared_data('original_name')
                    if stored_original and original_name == stored_original:
                        new_name = _config.load_nickname_from_config()
                        print_debug("AccountModel.getUserName: changed '%s' -> '%s'" % (original_name, new_name))
                        return new_name
                
                return original_name
                
            except Exception as e:
                print_error("Failed to load nickname from config, using original: %s" % str(e))
                return _original_AccountModel_setUserName(self, name)
        AccountModel.setUserName = _patched_AccountModel_setUserName
        
        print_debug("Patched AccountModel.setUserName successfully")
        
    except Exception as e:
        print_error("Failed to patch AccountModel: %s" % str(e))
        if _original_AccountModel_setUserName:
            try:
                original_fake_name = original_getFakeUserName(self)
                
                myDBID = getAccountDatabaseID()
                if myDBID is None:
                    print_debug("Account DBID is None, returning original fake name")
                    return original_fake_name
                
                model_dbid = self.getDatabaseID()
                
                if model_dbid == myDBID:
                    stored_original = get_shared_data('original_name')
                    if stored_original and original_fake_name == stored_original:
                        new_name = _config.load_nickname_from_config()
                        print_debug("AccountModel.getFakeUserName: changed '%s' -> '%s'" % (original_fake_name, new_name))
                        return new_name
                
                return original_fake_name
                
            except Exception as e:
                print_error("Failed to load nickname from config, using original: %s" % str(e))
                return _original_UserNameModel_setUserName(self, name)

        UserNameModel.setUserName = _patched_UserNameModel_setUserName
        
        print_debug("Patched UserNameModel.setUserName successfully")
        
    except Exception as e:
        print_error("Failed to patch UserNameModel: %s" % str(e))
        if _original_UserNameModel_setUserName:
            try:
                from gui.impl.gen.view_models.common.user_name_model import UserNameModel
                UserNameModel.setUserName = _original_UserNameModel_setUserName
            except:
                pass
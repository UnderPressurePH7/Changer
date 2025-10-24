# -*- coding: utf-8 -*-
import BigWorld
from ..utils import print_debug, print_error, get_shared_data

try:
    unicode
except NameError:
    unicode = str

def patch():
    print_debug("Starting models patches...")
    
    patch_account_model()
    patch_user_name_model()
    
    print_debug("All models patches applied")


def patch_account_model():
    try:
        from gui.impl.gen.view_models.common.account_model import AccountModel
        
        if hasattr(AccountModel, '_original_getUserName'):
            print_debug("AccountModel.getUserName already patched, skipping")
            return
        
        original_getUserName = AccountModel.getUserName
        
        def patched_getUserName(self):
            try:
                original_name = original_getUserName(self)
                
                myDBID = get_shared_data('accountDBID')
                if myDBID is None:
                    print_debug("Account DBID is None, returning original name")
                    return original_name
                
                model_dbid = self.getDatabaseID()
                
                if model_dbid == myDBID:
                    stored_original = get_shared_data('original_name')
                    if stored_original and original_name == stored_original:
                        new_name = get_shared_data('new_name')
                        print_debug("AccountModel.getUserName: changed '%s' -> '%s'" % (original_name, new_name))
                        return new_name
                
                return original_name
                
            except Exception as e:
                print_error("Error in patched getUserName: %s" % str(e))
                return original_getUserName(self)
        
        AccountModel._original_getUserName = original_getUserName
        AccountModel.getUserName = patched_getUserName
        print_debug("Patched AccountModel.getUserName successfully")
        
    except ImportError:
        print_debug("AccountModel not available")
    except Exception as e:
        print_error("Failed to patch AccountModel: %s" % str(e))


def patch_user_name_model():
    try:
        from gui.impl.gen.view_models.common.user_name_model import UserNameModel
        
        if hasattr(UserNameModel, '_original_getUserName'):
            print_debug("UserNameModel.getUserName already patched, skipping")
            return
        
        original_getUserName = UserNameModel.getUserName
        
        def patched_getUserName(self):
            try:
                original_name = original_getUserName(self)
                
                stored_original = get_shared_data('original_name')
                if stored_original and original_name == stored_original:
                    new_name = get_shared_data('new_name')
                    print_debug("UserNameModel.getUserName: changed '%s' -> '%s'" % (original_name, new_name))
                    return new_name
                
                return original_name
                
            except Exception as e:
                print_error("Error in patched UserNameModel.getUserName: %s" % str(e))
                return original_getUserName(self)
        
        UserNameModel._original_getUserName = original_getUserName
        UserNameModel.getUserName = patched_getUserName
        print_debug("Patched UserNameModel.getUserName successfully")
        
    except ImportError:
        print_debug("UserNameModel not available")
    except Exception as e:
        print_error("Failed to patch UserNameModel: %s" % str(e))
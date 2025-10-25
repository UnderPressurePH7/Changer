# -*- coding: utf-8 -*-
from ..utils import print_debug, print_error, get_shared_data

try:
    unicode
except NameError:
    unicode = str

def patch():
    
    print_debug("Starting notifications patches...")
    
    patch_notification_formatters()
    patch_achievement_formatters()
    patch_system_messages()
    
    print_debug("Notifications patches applied")


def patch_notification_formatters():
    try:
        from notification.decorators import MessageDecorator
        
        if hasattr(MessageDecorator, '_original_getListVO'):
            print_debug("MessageDecorator already patched, skipping")
            return
        
        if not hasattr(MessageDecorator, 'getListVO'):
            print_debug("MessageDecorator.getListVO not found")
            return
        
        original_getListVO = MessageDecorator.getListVO
        
        def patched_getListVO(self, *args, **kwargs):
            result = original_getListVO(self, *args, **kwargs)
            
            try:
                if isinstance(result, dict):
                    original_name = get_shared_data('original_name')
                    if original_name:
                        new_name = get_shared_data('new_name')
                        
                        for key in ('message', 'description', 'text', 'userName'):
                            if key in result and isinstance(result[key], (str, unicode)):
                                if original_name in result[key]:
                                    result[key] = result[key].replace(original_name, new_name)
                                    print_debug("Notification: name changed in %s" % key)
            except Exception as e:
                print_error("Error in patched getListVO: %s" % str(e))
            
            return result
        
        MessageDecorator._original_getListVO = original_getListVO
        MessageDecorator.getListVO = patched_getListVO
        print_debug("MessageDecorator.getListVO patched successfully")
        
    except ImportError:
        print_debug("MessageDecorator not available")
    except Exception as e:
        print_error("Failed to patch MessageDecorator: %s" % str(e))


def patch_achievement_formatters():
    try:
        from gui.server_events.formatters import AWARD_SHEET_KEYS
        from gui.shared.notifications import NotificationPriorityLevel
        from gui.shared.formatters import text_styles
        
        try:
            from gui.shared.formatters.servers_formatters import makeServerNameVO
            
            if hasattr(makeServerNameVO, '__call__') and not hasattr(makeServerNameVO, '_original'):
                original_makeServerNameVO = makeServerNameVO
                
                def patched_makeServerNameVO(serverName, *args, **kwargs):
                    result = original_makeServerNameVO(serverName, *args, **kwargs)
                    
                    try:
                        original_name = get_shared_data('original_name')
                        if original_name and isinstance(result, dict):
                            if 'label' in result and original_name in str(result['label']):
                                new_name = get_shared_data('new_name')
                                result['label'] = str(result['label']).replace(original_name, new_name)
                    except Exception as e:
                        print_error("Error in patched makeServerNameVO: %s" % str(e))
                    
                    return result
                
                print_debug("makeServerNameVO found but cannot patch (function)")
        except ImportError:
            print_debug("makeServerNameVO not available")
        
        print_debug("Achievement formatters checked")
        
    except ImportError:
        print_debug("Achievement formatters not available")
    except Exception as e:
        print_error("Failed to patch achievement formatters: %s" % str(e))


def patch_system_messages():
    try:
        from messenger.formatters.service_channel import ServiceChannelFormatter
        
        if not hasattr(ServiceChannelFormatter, 'format'):
            print_debug("ServiceChannelFormatter.format not found")
            return
        
        if hasattr(ServiceChannelFormatter, '_original_format'):
            print_debug("ServiceChannelFormatter already patched, skipping")
            return
        
        original_format = ServiceChannelFormatter.format
        
        def patched_format(self, message, *args, **kwargs):
            result = original_format(self, message, *args, **kwargs)
            
            try:
                original_name = get_shared_data('original_name')
                if original_name:
                    new_name = get_shared_data('new_name')
                    
                    if isinstance(result, dict):
                        for key in ('message', 'text', 'data'):
                            if key in result:
                                if isinstance(result[key], (str, unicode)):
                                    if original_name in result[key]:
                                        result[key] = result[key].replace(original_name, new_name)
                                        print_debug("System message: name changed in %s" % key)
                                elif isinstance(result[key], dict):

                                    for subkey, subval in result[key].items():
                                        if isinstance(subval, (str, unicode)) and original_name in subval:
                                            result[key][subkey] = subval.replace(original_name, new_name)
                    

                    elif isinstance(result, (str, unicode)) and original_name in result:
                        result = result.replace(original_name, new_name)
                        print_debug("System message: name changed in string result")
            
            except Exception as e:
                print_error("Error in patched format: %s" % str(e))
            
            return result
        
        ServiceChannelFormatter._original_format = original_format
        ServiceChannelFormatter.format = patched_format
        print_debug("ServiceChannelFormatter.format patched successfully")
        
    except ImportError:
        print_debug("ServiceChannelFormatter not available")
    except Exception as e:
        print_error("Failed to patch ServiceChannelFormatter: %s" % str(e))
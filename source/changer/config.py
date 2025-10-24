# -*- coding: utf-8 -*-
import os
import json
import re
try:
    unicode
except NameError:
    unicode = str
from .utils import print_debug, print_error

class Config(object):
    def __init__(self):
        self.config_path = 'mods/configs/under_pressure/changer.json'
        self._cached_nickname = None
        self._ensure_config_exists()

    def _ensure_config_exists(self):
        try:
            config_dir = os.path.dirname(self.config_path)
            if not os.path.exists(config_dir):
                os.makedirs(config_dir)
            if not os.path.exists(self.config_path):
                self._create_default_config()
        except Exception as e:
            print_error("Error ensuring config exists: %s" % str(e))

    def _create_default_config(self):
        try:
            config_data = {"nickName": "BOSS"}
            with open(self.config_path, 'w') as f:
                json.dump(config_data, f, indent=4)
            print_debug("Default config created")
        except Exception as e:
            print_error("Error creating default config: %s" % str(e))

    def _validate_nickname(self, nickname):
        if not nickname:
            return False, "Nickname is empty"
        
        if not isinstance(nickname, (str, unicode)):
            return False, "Nickname must be a string"
        
        nickname_str = unicode(nickname)
        
        if len(nickname_str) < 3:
            return False, "Nickname too short (min 3 characters)"
        
        if len(nickname_str) > 24:
            return False, "Nickname too long (max 24 characters)"
        
        if not re.match(r'^[a-zA-Z0-9_-]+$', nickname_str):
            return False, "Nickname contains invalid characters (only letters, numbers, _, - allowed)"
        
        if nickname_str[0] in '_-' or nickname_str[-1] in '_-':
            return False, "Nickname cannot start or end with _ or -"
        
        return True, None

    def load_nickname_from_config(self):
        if self._cached_nickname is not None:
            return self._cached_nickname
        
        try:
            with open(self.config_path, 'r') as f:
                config_data = json.load(f)
                nickname = config_data.get('nickName')
                
                is_valid, error_msg = self._validate_nickname(nickname)
                
                if not is_valid:
                    print_error("Invalid nickname in config: %s. Using default 'BOSS'" % error_msg)
                    self._cached_nickname = u"BOSS"
                    return self._cached_nickname
                
                self._cached_nickname = unicode(nickname)
                print_debug("Nickname loaded from config: %s" % self._cached_nickname)
                return self._cached_nickname
                
        except Exception as e:
            print_error("Error loading config: %s" % str(e))
            self._cached_nickname = u"BOSS"
            return self._cached_nickname
    
    def reload_config(self):
        self._cached_nickname = None
        return self.load_nickname_from_config()
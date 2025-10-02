# -*- coding: utf-8 -*-
import os
import json
try:
    unicode
except NameError:
    unicode = str
from .utils import print_log, print_debug, print_error

class Config(object):
    def __init__(self):
        self.config_path = 'mods/configs/under_pressure/changer.json'
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

    def load_nickname_from_config(self):
        try:
            with open(self.config_path, 'r') as f:
                config_data = json.load(f)
                nickname = config_data.get('nickName')
                print_debug("Nickname loaded from config: %s" % nickname)
                return unicode(nickname)
        except Exception as e:
            print_error("Error loading config: %s" % str(e))
            return u"BOSS"
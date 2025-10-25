# -*- coding: utf-8 -*-
import BigWorld
from PlayerEvents import g_playerEvents
from account_helpers import getAccountDatabaseID

from .utils import print_debug, print_error, set_shared_data, get_shared_data


class AccountDBID(object):

    def __init__(self):
        self._accountDBID = None
        g_playerEvents.onAccountShowGUI += self.onAccountShowGUI

    def finalize(self):
        g_playerEvents.onAccountShowGUI -= self.onAccountShowGUI

    def onAccountShowGUI(self, *args):
        try:
            player = BigWorld.player()
            if player and hasattr(player, 'databaseID'):
                if not get_shared_data('accountDBID'):
                    self._accountDBID = getAccountDatabaseID() or player.databaseID
                    set_shared_data('accountDBID', self._accountDBID)
                    print_debug("Account DBID obtained: %s" % str(self._accountDBID))
                
                if not get_shared_data('original_name') and hasattr(player, 'name'):
                    print_debug("Warning: original_name not set by account_patch, setting from player")
                    set_shared_data('original_name', player.name)
            else:
                print_debug("Player not ready, retrying in 1 second")
                BigWorld.callback(1, self.onAccountShowGUI)
        except Exception as e:
            print_error("Error obtaining Account DBID: %s" % str(e))
            BigWorld.callback(1, self.onAccountShowGUI)

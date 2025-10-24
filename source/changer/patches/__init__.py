# -*- coding: utf-8 -*-

__all__ = ['apply_patches']

def apply_patches(config):
    from . import account_patch
    from . import battle_patch
    from . import lobby_vo_patch
    from . import lobby_chat_patch
    from . import models_patch
    from . import battle_results_patch
    from . import stats_patch
    from . import notifications_patch
    from . import clan_patch
    
    account_patch.patch(config)
    
    battle_patch.patch()
    battle_results_patch.patch()
    lobby_vo_patch.patch()
    lobby_chat_patch.patch()
    models_patch.patch()
    stats_patch.patch()
    notifications_patch.patch()
    clan_patch.patch()
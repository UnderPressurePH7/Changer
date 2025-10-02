# -*- coding: utf-8 -*-

__all__ = ['apply_patches']

def apply_patches(config):
    from . import account_patch
    from . import profile_patch
    from . import battle_patch
    from . import lobby_vo_patch
    from . import lobby_chat_patch
    
    account_patch.patch(config)
    profile_patch.patch(config)
    battle_patch.patch(config)
    lobby_vo_patch.patch(config)
    lobby_chat_patch.patch(config)
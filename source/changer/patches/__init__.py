# -*- coding: utf-8 -*-

__all__ = ['apply_patches']

def apply_patches(config):
    from . import account_patch
    from . import profile_patch
    from . import battle_patch
    from . import vo_patch
    
    account_patch.patch(config)
    profile_patch.patch(config)
    battle_patch.patch(config)
    vo_patch.patch(config)
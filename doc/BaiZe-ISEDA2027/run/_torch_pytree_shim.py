#!/usr/bin/env python3
"""
Torch _pytree.register_constant shim for torch < 2.7.

transformers >= 4.50 uses torch.utils._pytree.register_constant,
which was added in torch 2.7. On torch 2.6.0+cu124 (the last version
supporting CUDA 12.4), this attribute is missing.

This shim adds a no-op register_constant so transformers can import
without crashing. It is safe for inference/serving workloads where
pytree constant registration is not exercised.
"""
import torch.utils._pytree as _pytree

if not hasattr(_pytree, "register_constant"):
    def _register_constant(cls, module_name=None):
        # No-op: torch < 2.7 doesn't support pytree constant registration.
        # This is only used by transformers for advanced pytree handling
        # of constant types, which is not needed for basic inference.
        return cls
    _pytree.register_constant = _register_constant

#!/usr/bin/env python3
"""Dump the exact HF NemotronH state_dict key names (meta device) to confirm the
conversion mapping. Run with the transformers 5.17.0 --target dir on sys.path."""
import sys
sys.path.insert(0, "/nas_train/app.e0031982/code/BaiZe-ISEDA2027/p6_tf5")

import torch
from transformers import NemotronHConfig, NemotronHModel

pat = "M-M-M--M-M*-M-M-M-M--M*-M-M-M-M-M*--M-M-M-M-M*-M--M-M-M-"
mp = {"M": "linear_attention", "*": "full_attention", "-": "mlp"}
lt = [mp[c] for c in pat]
print("num layers", len(lt))

cfg = NemotronHConfig(
    vocab_size=129408, hidden_size=2048, layers_block_type=lt,
    num_attention_heads=16, num_key_value_heads=4, head_dim=128,
    intermediate_size=8192, mlp_hidden_act="gelu", mlp_bias=False,
    ssm_state_size=128, mamba_num_heads=64, mamba_head_dim=64, mamba_hidden_act="silu",
    n_groups=8, conv_kernel=4, expand=2, use_conv_bias=True, mamba_proj_bias=False,
    chunk_size=128, time_step_min=0.001, time_step_max=0.1, time_step_floor=1e-4,
    max_position_embeddings=4096, layer_norm_epsilon=1e-5,
    rescale_prenorm_residual=False, tie_word_embeddings=False, use_cache=True,
)
print("OK cfg; layers_block_type[0:5] =", cfg.layers_block_type[:5])

with torch.device("meta"):
    m = NemotronHModel(cfg)
sd = m.state_dict()
keys = list(sd.keys())
print("TOTAL KEYS", len(keys))
for k in keys:
    print(k, tuple(sd[k].shape))
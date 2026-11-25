#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""校验 1M 位置编码配置（用户令 2026-10-26：56 层中 4 层注意力的 RoPE max position = 1M）。

检查项（全部可覆盖）：
  1. 层数 = 56
  2. 全注意力层 = 4（其余 24 Mamba2 + 28 MLP，Nemotron-H 式）
  3. max_position_embeddings = 1,048,576（1M = 2^20）
  4. rope_theta = 1,000,000（ABF；⚠️ 只抬 max_pos 不抬 theta ⇒ 实测全 NaN）
  5. rope_scaling 为空/None（训练期不启 PI/NTK/YaRN）

用法::

    python check_rope.py --config /path/to/config.json
    python check_rope.py --hf-dir nemo_experiments/baize2b/hf_iter_2000
    python check_rope.py --config c.json --expect-maxpos 1048576 --expect-theta 1000000

退出码：0=全通过 / 1=有不符 / 2=文件或字段缺失。
"""
from __future__ import annotations

import argparse
import json
import os
import sys

ATTN = {"attention", "full_attention", "attn", "*"}
MAMBA = {"mamba", "mamba2", "linear_attention", "ssm", "m"}
MLP = {"mlp", "-", "ffn"}


def load(path: str) -> dict:
    # utf-8-sig 兼容带 BOM 的 config（Windows 工具导出常见），Linux 无 BOM 时等价 utf-8
    with open(path, encoding="utf-8-sig") as f:
        return json.load(f)


def layers_of(cfg: dict):
    """返回逐层类型列表；来源优先级 layers_block_type > hybrid_override_pattern。"""
    lb = cfg.get("layers_block_type")
    if isinstance(lb, list) and lb:
        return [str(x).lower() for x in lb], "layers_block_type"
    pat = cfg.get("hybrid_override_pattern") or cfg.get("hybrid_layer_pattern")
    if isinstance(pat, str) and pat:
        chars = [c for c in pat if c != " "]
        return [c.lower() for c in chars], "hybrid_override_pattern"
    return None, "none"


def classify(t: str) -> str:
    if t in ATTN or t.startswith("attention"):
        return "attention"
    if t in MAMBA or t.startswith("mamba"):
        return "mamba"
    if t in MLP or t in ("-",):
        return "mlp"
    return "unknown"


def main() -> None:
    ap = argparse.ArgumentParser(description="校验 1M RoPE 配置")
    ap.add_argument("--config", help="config.json 路径")
    ap.add_argument("--hf-dir", help="HF 目录（自动找 config.json）")
    ap.add_argument("--expect-layers", type=int, default=56)
    ap.add_argument("--expect-attn", type=int, default=4)
    ap.add_argument("--expect-maxpos", type=int, default=1048576)
    ap.add_argument("--expect-theta", type=float, default=1000000.0)
    args = ap.parse_args()

    path = args.config
    if not path and args.hf_dir:
        path = os.path.join(args.hf_dir, "config.json")
    if not path or not os.path.isfile(path):
        print(f"FAIL: 找不到 config：{path}", file=sys.stderr)
        sys.exit(2)
    try:
        cfg = load(path)
    except (OSError, json.JSONDecodeError) as e:
        print(f"FAIL: 读不了/解析不了 {path}：{e}", file=sys.stderr)
        sys.exit(2)

    fails = []
    layers, src = layers_of(cfg)
    n_layers = cfg.get("num_hidden_layers") or cfg.get("num_layers") or (len(layers) if layers else None)
    maxpos = cfg.get("max_position_embeddings")
    theta = cfg.get("rope_theta")
    scaling = cfg.get("rope_scaling")

    print(f"===== check_rope @ {path} =====")
    print(f"  num_hidden_layers        : {n_layers}")
    print(f"  max_position_embeddings  : {maxpos}")
    print(f"  rope_theta               : {theta}")
    print(f"  rope_scaling             : {scaling!r}")
    print(f"  层类型来源               : {src}")

    if n_layers != args.expect_layers:
        fails.append(f"层数 {n_layers} != {args.expect_layers}")
    if not layers:
        fails.append("找不到 layers_block_type / hybrid_override_pattern，无法核对注意力层数")
    else:
        kinds = [classify(t) for t in layers]
        n_attn = kinds.count("attention")
        n_ssm = kinds.count("mamba")
        n_mlp = kinds.count("mlp")
        n_unk = kinds.count("unknown")
        attn_idx = [i for i, k in enumerate(kinds) if k == "attention"]
        print(f"  层构成                   : attention={n_attn}  mamba2={n_ssm}  mlp={n_mlp}  unknown={n_unk}")
        print(f"  注意力层下标(0-based)    : {attn_idx}")
        if n_attn != args.expect_attn:
            fails.append(f"注意力层数 {n_attn} != {args.expect_attn}")
        if n_unk:
            fails.append(f"有 {n_unk} 层类型无法识别（{set(k for k in kinds if k == 'unknown')}）")
        if len(layers) != args.expect_layers:
            fails.append(f"层类型串长度 {len(layers)} != {args.expect_layers}")

    if maxpos != args.expect_maxpos:
        fails.append(f"max_position_embeddings={maxpos} != {args.expect_maxpos}")
    if theta is None or abs(float(theta) - args.expect_theta) > 1e-6:
        fails.append(f"rope_theta={theta} != {args.expect_theta:g}（⚠️ 只抬 max_pos 会 NaN）")
    if scaling not in (None, {}, ""):
        fails.append(f"rope_scaling 非空：{scaling!r}（本计划训练期不启用）")

    print()
    if fails:
        for f in fails:
            print(f"  ✗ {f}")
        print(f"结论：FAIL（{len(fails)} 项）")
        sys.exit(1)
    print("结论：PASS —— 56 层 / 4 层注意力 / max_pos=1M / theta=1e6 / 无 rope_scaling")


if __name__ == "__main__":
    main()

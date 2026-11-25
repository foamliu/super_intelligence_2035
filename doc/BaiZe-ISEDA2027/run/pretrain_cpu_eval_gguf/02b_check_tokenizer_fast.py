#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""02b_check_tokenizer_fast.py — numpy-free 版 02_check_tokenizer.py。

为什么需要它：
  02_check_tokenizer.py 用 ``from transformers import AutoTokenizer``，而 py310 env
  里 torch 是按 numpy 2.x ABI 编译的、运行时 numpy=1.26.4，触发
  "numpy.dtype size changed" 异常，导致 ``import transformers`` 直接失败。
  但 HF 的 ``AutoTokenizer`` 底层就是 ``tokenizers.Tokenizer``（纯 Rust，不依赖 numpy），
  所以本脚本直接用 ``tokenizers`` 读 tokenizer.json，与 02 逻辑完全等价，却绕开 numpy。

判据与 02 完全一致：12 条中/英/混排/代码样例 × {add_special True/False}，
GGUF(llama-server /tokenize) vs HF(tokenizer.json) 逐 token id 对拍，全一致才 PASS。

用法:
  python3 02b_check_tokenizer_fast.py <hf_dir> [--base-url http://127.0.0.1:8080]
  # 退出码 0 = 全一致；1 = 有不一致；2 = 无法完成检查
"""
import argparse
import json
import sys
import urllib.request

SAMPLES = [
    "The capital of France is",
    "Question: Which of the following is a mammal?\nAnswer:",
    "长城是中国的象征，它始建于",
    "半导体制造中的光刻工艺决定了",
    "我们用 Mamba2 hybrid 架构，seq_length=4096。",
    "def add(a, b):\n    return a + b",
    "import torch\nx = torch.zeros(2, 3)",
    "x^2 + y^2 = r^2, where r >= 0",
    "hello world",
    " hello world",
    "hello  world\n\nnext line",
    "2026-11-03 19:49:07",
]


def post_json(url, payload, timeout=30):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"}, method="POST"
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def server_tokenize(base_url, text, add_special):
    out = post_json(
        base_url.rstrip("/") + "/tokenize",
        {"content": text, "add_special": bool(add_special), "parse_special": True},
    )
    toks = out.get("tokens")
    if toks is None:
        raise RuntimeError(f"/tokenize 返回无 tokens: {out}")
    return [int(t["id"]) if isinstance(t, dict) else int(t) for t in toks]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("hf_dir")
    ap.add_argument("--base-url", default="http://127.0.0.1:8080")
    ap.add_argument("--max-report", type=int, default=5)
    args = ap.parse_args()

    try:
        from tokenizers import Tokenizer
    except Exception as e:  # noqa: BLE001
        print(f"[check-fast] FAIL: 无法 import tokenizers: {e}", file=sys.stderr)
        return 2

    import os
    tok_path = os.path.join(args.hf_dir, "tokenizer.json")
    if not os.path.isfile(tok_path):
        print(f"[check-fast] FAIL: 缺 {tok_path}", file=sys.stderr)
        return 2
    try:
        tok = Tokenizer.from_file(tok_path)
    except Exception as e:  # noqa: BLE001
        print(f"[check-fast] FAIL: 无法加载 tokenizer.json: {e}", file=sys.stderr)
        return 2
    print(f"[check-fast] HF tokenizer = {tok_path} (tokenizers lib, numpy-free)")

    try:
        with urllib.request.urlopen(args.base_url.rstrip("/") + "/health", timeout=10) as r:
            health = r.read().decode("utf-8", "ignore")
    except Exception as e:  # noqa: BLE001
        print(f"[check-fast] FAIL: llama-server 不可达 {args.base_url}: {e}", file=sys.stderr)
        return 2
    print(f"[check-fast] server health: {health.strip()[:120]}")

    bad = 0
    for add_special in (True, False):
        for s in SAMPLES:
            try:
                hf_ids = tok.encode(s, add_special_tokens=add_special).ids
                gg_ids = server_tokenize(args.base_url, s, add_special)
            except Exception as e:  # noqa: BLE001
                print(f"[check-fast] ERROR add_special={add_special} text={s!r}: {e}", file=sys.stderr)
                bad += 1
                continue
            if hf_ids != gg_ids:
                bad += 1
                if bad <= args.max_report:
                    print(
                        f"[check-fast] MISMATCH add_special={add_special} text={s!r}\n"
                        f"        hf={hf_ids}\n"
                        f"        gg={gg_ids}",
                        file=sys.stderr,
                    )

    total = len(SAMPLES) * 2
    if bad:
        print(
            f"[check-fast] FAIL: {bad}/{total} 不一致。"
            "请换用包含 PR #30960 的 llama.cpp master，或检查 GGUF 的 tokenizer.ggml.pre。",
            file=sys.stderr,
        )
        return 1

    print(f"[check-fast] PASS: {total}/{total} 条样例 token id 完全一致")
    return 0


if __name__ == "__main__":
    sys.exit(main())

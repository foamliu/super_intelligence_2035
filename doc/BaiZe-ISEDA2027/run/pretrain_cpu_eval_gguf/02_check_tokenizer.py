#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""02_check_tokenizer.py — GGUF(llama-server) 分词 vs HF 分词，逐 token id 对拍。

为什么必须做：
  llama.cpp 曾把 Nemotron 系的 Tekken 分词错标成 pixtral（issue #30894 /
  PR #30960），会导致中英之外文本 token 数不同。分词不一致 => loglikelihood
  的 token 边界全错 => 分数不可用。本脚本是切换 GGUF 的硬门槛。

用法:
  python3 02_check_tokenizer.py <hf_dir> [--base-url http://127.0.0.1:8080]
  # 退出码 0 = 全一致；1 = 有不一致；2 = 无法完成检查

注意:
  - 只读 HF tokenizer（AutoTokenizer, local_files_only），不加载权重。
  - 不依赖 GPU。
"""
import argparse
import json
import sys
import urllib.request

SAMPLES = [
    # 英文
    "The capital of France is",
    "Question: Which of the following is a mammal?\nAnswer:",
    # 中文
    "长城是中国的象征，它始建于",
    "半导体制造中的光刻工艺决定了",
    # 中英混排
    "我们用 Mamba2 hybrid 架构，seq_length=4096。",
    # 代码
    "def add(a, b):\n    return a + b",
    "import torch\nx = torch.zeros(2, 3)",
    # 数学 / 符号
    "x^2 + y^2 = r^2, where r >= 0",
    # 空白与换行（BPE 边界最容易出问题）
    "hello world",
    " hello world",
    "hello  world\n\nnext line",
    # 数字
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
    # with_pieces=false 时是 int 数组
    return [int(t["id"]) if isinstance(t, dict) else int(t) for t in toks]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("hf_dir")
    ap.add_argument("--base-url", default="http://127.0.0.1:8080")
    ap.add_argument("--max-report", type=int, default=5, help="最多打印几条不一致明细")
    args = ap.parse_args()

    try:
        from transformers import AutoTokenizer
    except Exception as e:  # noqa: BLE001
        print(f"[check] FAIL: 无法 import transformers: {e}", file=sys.stderr)
        return 2

    try:
        tok = AutoTokenizer.from_pretrained(
            args.hf_dir, trust_remote_code=False, local_files_only=True
        )
    except Exception as e:  # noqa: BLE001
        print(f"[check] FAIL: 无法加载 HF tokenizer: {e}", file=sys.stderr)
        print(
            "[check] 提示：如需 NemotronH 自定义 tokenizer，"
            "请先 export PYTHONPATH=/nas_train/app.e0031982/code/BaiZe-ISEDA2027/p6_tf5:$PYTHONPATH",
            file=sys.stderr,
        )
        return 2

    # 先确认 server 活着
    try:
        with urllib.request.urlopen(args.base_url.rstrip("/") + "/health", timeout=10) as r:
            health = r.read().decode("utf-8", "ignore")
    except Exception as e:  # noqa: BLE001
        print(f"[check] FAIL: llama-server 不可达 {args.base_url}: {e}", file=sys.stderr)
        return 2
    print(f"[check] server health: {health.strip()[:120]}")

    bad = 0
    for add_special in (True, False):
        for s in SAMPLES:
            try:
                hf_ids = tok.encode(s, add_special_tokens=add_special)
                gg_ids = server_tokenize(args.base_url, s, add_special)
            except Exception as e:  # noqa: BLE001
                print(f"[check] ERROR add_special={add_special} text={s!r}: {e}", file=sys.stderr)
                bad += 1
                continue
            if hf_ids != gg_ids:
                bad += 1
                if bad <= args.max_report:
                    print(
                        f"[check] MISMATCH add_special={add_special} text={s!r}\n"
                        f"        hf={hf_ids}\n"
                        f"        gg={gg_ids}",
                        file=sys.stderr,
                    )

    total = len(SAMPLES) * 2
    if bad:
        print(
            f"[check] FAIL: {bad}/{total} 不一致。"
            "请换用包含 PR #30960 的 llama.cpp master，或检查 GGUF 的 tokenizer.ggml.pre。",
            file=sys.stderr,
        )
        return 1

    print(f"[check] PASS: {total}/{total} 条样例 token id 完全一致")
    return 0


if __name__ == "__main__":
    sys.exit(main())

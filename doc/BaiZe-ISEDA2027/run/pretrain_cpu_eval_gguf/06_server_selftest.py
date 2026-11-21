#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""06_server_selftest.py — 校验 llama-server 是否满足本方案依赖的 3 个契约。

契约:
  1. /tokenize 可用，且返回 int token 数组；
  2. /completion 接受 **prompt = token id 数组**（不是字符串）；
  3. /completion 接受 logit_bias=[[token_id, bias], ...] 且 n_probs>0 时
     返回 completion_probabilities[0]={id, logprob, top_logprobs}，
     被强制的目标 token 的 id 与请求一致。

用法:
  python3 06_server_selftest.py [--base-url http://127.0.0.1:8080]

退出码: 0 = 三个契约全过；1 = 有契约不满足；2 = 连不上。
"""
import argparse
import json
import sys
import urllib.request


def post(url, payload, timeout=60):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"}, method="POST"
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def get(url, timeout=30):
    with urllib.request.urlopen(url, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", default="http://127.0.0.1:8080")
    ap.add_argument("--text", default="The capital of France is Paris")
    args = ap.parse_args()
    base = args.base_url.rstrip("/")

    # 0) 连通性
    try:
        props = get(base + "/props")
    except Exception as e:  # noqa: BLE001
        print(f"[selftest] FAIL: /props 不可达: {e}", file=sys.stderr)
        return 2
    print(f"[selftest] model={props.get('model_path') or props.get('model_alias')} "
          f"n_ctx={props.get('default_generation_settings', {}).get('n_ctx')}")

    # 1) tokenize
    try:
        tok = post(base + "/tokenize", {"content": args.text, "add_special": True})
        ids = tok["tokens"]
        ids = [int(t["id"]) if isinstance(t, dict) else int(t) for t in ids]
    except Exception as e:  # noqa: BLE001
        print(f"[selftest] FAIL: /tokenize 失败: {e}", file=sys.stderr)
        return 1
    if len(ids) < 3:
        print(f"[selftest] FAIL: token 数异常: {ids}", file=sys.stderr)
        return 1
    print(f"[selftest] tokenize OK: {len(ids)} tokens, head={ids[:5]}")

    # 2)+3) prompt=ids + logit_bias + n_probs
    prompt_ids, target = ids[:-1], ids[-1]
    payload = {
        "prompt": [int(x) for x in prompt_ids],
        "n_predict": 1,
        "temperature": 0.0,
        "top_k": 1,
        "n_probs": 10,
        "logit_bias": [[int(target), 100.0]],
        "cache_prompt": True,
        "return_tokens": True,
        "stream": False,
    }
    try:
        resp = post(base + "/completion", payload)
    except Exception as e:  # noqa: BLE001
        print(f"[selftest] FAIL: /completion(token-id prompt) 失败: {e}", file=sys.stderr)
        print("[selftest] 若 HTTP 400 且提示 prompt 类型，说明该版本不支持 token id 数组，"
              "需要改用字符串 prompt 方案（本 pilot 需调整）。", file=sys.stderr)
        return 1

    probs = resp.get("completion_probabilities") or []
    if not probs:
        print(f"[selftest] FAIL: 无 completion_probabilities: {str(resp)[:400]}", file=sys.stderr)
        return 1
    entry = probs[0]
    got = int(entry.get("id", -1))
    lp = entry.get("logprob")
    tops = entry.get("top_logprobs") or []
    print(f"[selftest] completion OK: forced id={got} target={target} "
          f"logprob={lp} top_logprobs={len(tops)}")
    if got != target:
        print("[selftest] FAIL: logit_bias 未强制成功（可能 bias 不够或接口忽略该字段）",
              file=sys.stderr)
        return 1
    if not isinstance(lp, (int, float)):
        print("[selftest] FAIL: logprob 非数值", file=sys.stderr)
        return 1

    # 4) 重复一次：验证 cache_prompt 不会改变结果
    try:
        resp2 = post(base + "/completion", payload)
        lp2 = resp2["completion_probabilities"][0]["logprob"]
    except Exception as e:  # noqa: BLE001
        print(f"[selftest] WARN: 第二次请求失败: {e}", file=sys.stderr)
        lp2 = None
    if lp2 is not None:
        diff = abs(float(lp2) - float(lp))
        print(f"[selftest] repeat logprob={lp2} |diff|={diff:.6f}")
        if diff > 1e-3:
            print("[selftest] WARN: 两次结果不一致（可能 cache_prompt 引起），"
                  "对选择题影响很小，但请在报告里注明。", file=sys.stderr)

    print("[selftest] PASS: tokenize / token-id prompt / logit_bias / n_probs 全部可用")
    return 0


if __name__ == "__main__":
    sys.exit(main())

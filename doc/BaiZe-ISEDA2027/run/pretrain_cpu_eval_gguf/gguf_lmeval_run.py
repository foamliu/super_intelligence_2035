#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gguf_lmeval_run.py — 用 llama-server 给 lm_eval 提供 loglikelihood 后端。

为什么不用 lm_eval 0.4.13 自带的 ``--model gguf``：
  该版本走 legacy logprobs（token_logprobs / text_offset），而 2025 年后的
  llama.cpp 只返回 OpenAI 风格的 logprobs.content，旧后端会直接 assert。
  这里按 lm_eval main 的思路自己实现：用 logit_bias 强制目标 token，读其
  logprob，逐 token 累加。

与 lm_eval main 的差异（也是本实现的优点）：
  * prompt 直接传 **token id 数组**（native /completion 支持），
    分词统一走 server /tokenize —— 避免 BPE 边界上的 token 错位；
  * 同一道题的多个候选 pin 到同一个 slot，复用 prompt cache；
  * 结果结构与 ``cpu_lmeval_run.py`` 完全一致（results.json），
    现有报告生成器可直接读。

用法:
  python3 gguf_lmeval_run.py \
      --base-url http://127.0.0.1:8080 \
      --hf-dir /path/hf_iter_10000 \
      --output /path/lm_eval_results/gguf_iter_10000 \
      --tasks arc_challenge,arc_easy,boolq,hellaswag,openbookqa,piqa,sciq,winogrande \
      [--limit 100] [--parallel 2] [--batch-size 32]
"""
import argparse
import json
import os
import sys
import time
import zlib
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

import requests
from tqdm import tqdm

from lm_eval import simple_evaluate
from lm_eval.api.model import TemplateLM

DEFAULT_TASKS = "arc_challenge,arc_easy,boolq,hellaswag,openbookqa,piqa,sciq,winogrande"


class GGUFServerLM(TemplateLM):
    """通过 llama-server 计算 loglikelihood 的 lm_eval 后端。"""

    def __init__(
        self,
        base_url,
        eot_token_id,
        parallel=2,
        max_length=2048,
        timeout=600,
        batch_size=32,
        max_prompt_tokens=0,
    ):
        super().__init__()
        self.base_url = base_url.rstrip("/")
        self._eot = int(eot_token_id)
        self.parallel = max(1, int(parallel))
        self._max_length = int(max_length)
        self._batch_size = int(batch_size)
        self._device = "cpu"
        self.timeout = int(timeout)
        self.max_prompt_tokens = int(max_prompt_tokens)  # 0 = 不额外截断

        self._local = threading.local()
        self._tok_cache = {}
        self._tok_lock = threading.Lock()
        self._stat_lock = threading.Lock()
        self.n_token_requests = 0
        self.n_docs = 0
        self.n_truncated = 0

    # ---------- lm_eval 需要的属性 ----------
    @property
    def eot_token_id(self):
        return self._eot

    @property
    def tokenizer_name(self):
        return "gguf-server"

    @property
    def batch_size(self):
        return self._batch_size

    @batch_size.setter
    def batch_size(self, value):
        try:
            self._batch_size = max(1, int(value))
        except (TypeError, ValueError):
            self._batch_size = 1

    @property
    def max_length(self):
        return self._max_length

    @max_length.setter
    def max_length(self, value):
        self._max_length = int(value)

    @property
    def device(self):
        return self._device

    # ---------- HTTP ----------
    def _post(self, path, payload, retries=3):
        url = self.base_url + path
        sess = getattr(self._local, "session", None)
        if sess is None:
            sess = requests.Session()
            self._local.session = sess
        last = None
        for attempt in range(retries):
            try:
                r = sess.post(url, json=payload, timeout=self.timeout)
                if r.status_code >= 400:
                    raise RuntimeError(f"HTTP {r.status_code}: {r.text[:400]}")
                return r.json()
            except Exception as e:  # noqa: BLE001
                last = e
                if attempt == retries - 1:
                    break
                time.sleep(1.5 * (attempt + 1))
        raise RuntimeError(f"POST {path} 失败（{retries} 次）: {last}")

    # ---------- 分词（统一走 server） ----------
    def tok_encode(self, string, add_special_tokens=None, **kwargs):
        # TemplateLM 语义：None => 加 special（与 HF backend 一致）
        add_special = True if add_special_tokens is None else bool(add_special_tokens)
        key = (string, add_special)
        with self._tok_lock:
            hit = self._tok_cache.get(key)
        if hit is not None:
            return list(hit)
        out = self._post(
            "/tokenize",
            {"content": string, "add_special": add_special, "parse_special": True},
        )
        toks = out.get("tokens")
        if toks is None:
            raise RuntimeError(f"/tokenize 返回无 tokens: {out}")
        ids = [int(t["id"]) if isinstance(t, dict) else int(t) for t in toks]
        with self._tok_lock:
            self._tok_cache[key] = list(ids)
        return ids

    # ---------- 单 token 打分 ----------
    def _score_token(self, prompt_ids, target_id, slot):
        payload = {
            "prompt": [int(x) for x in prompt_ids],
            "n_predict": 1,
            "temperature": 0.0,
            "top_k": 1,
            "top_p": 1.0,
            "min_p": 0.0,
            "n_probs": 10,
            # native /completion 的 logit_bias 期望 [[token_id, bias], ...]
            "logit_bias": [[int(target_id), 100.0]],
            "cache_prompt": True,
            "return_tokens": True,
            "id_slot": int(slot),
            "stream": False,
        }
        resp = self._post("/completion", payload)
        probs = resp.get("completion_probabilities") or []
        if not probs:
            raise RuntimeError(f"无 completion_probabilities: {str(resp)[:500]}")
        entry = probs[0]
        got = int(entry.get("id", -1))
        if got != int(target_id):
            raise RuntimeError(
                f"目标 token 未被强制：got={got} want={target_id} "
                f"（检查 llama.cpp 是否支持 logit_bias / n_probs）"
            )
        logprob = float(entry["logprob"])
        tops = entry.get("top_logprobs") or []
        greedy = bool(tops) and int(max(tops, key=lambda t: t["logprob"]).get("id", -1)) == int(target_id)
        with self._stat_lock:
            self.n_token_requests += 1
        return logprob, greedy

    # ---------- lm_eval 调用面 ----------
    def _loglikelihood_tokens(self, requests, disable_tqdm=False, **kwargs):
        """requests: [((ctx, cont), ctx_enc, cont_enc), ...]"""

        def work(item):
            (_pair, ctx_enc, cont_enc) = item
            ctx_ids = [int(x) for x in ctx_enc]
            cont_ids = [int(x) for x in cont_enc]
            if not cont_ids:
                return (0.0, True)

            # 防超长（llama-server 的 -c 是硬上限）
            limit = self.max_prompt_tokens or self._max_length
            if len(ctx_ids) + len(cont_ids) > limit:
                keep = max(0, limit - len(cont_ids))
                ctx_ids = ctx_ids[-keep:] if keep else []
                with self._stat_lock:
                    self.n_truncated += 1

            # 同一 context 的多个候选 -> 同一 slot，复用 prompt cache
            slot = zlib.crc32(json.dumps(ctx_ids).encode("utf-8")) % self.parallel
            total = 0.0
            greedy = True
            for j, target in enumerate(cont_ids):
                lp, g = self._score_token(ctx_ids + cont_ids[:j], target, slot)
                total += lp
                greedy = greedy and g
            with self._stat_lock:
                self.n_docs += 1
            return (float(total), bool(greedy))

        out = [None] * len(requests)
        with ThreadPoolExecutor(max_workers=self.parallel) as ex:
            futs = {ex.submit(work, item): i for i, item in enumerate(requests)}
            for fut in tqdm(
                as_completed(futs), total=len(futs), disable=disable_tqdm, desc="gguf-ll"
            ):
                out[futs[fut]] = fut.result()
        return out

    def loglikelihood_rolling(self, requests, disable_tqdm=False):
        raise NotImplementedError("GGUF 后端不支持 loglikelihood_rolling（8 个常识集不需要）")

    def generate_until(self, requests, disable_tqdm=False):
        raise NotImplementedError("GGUF 后端只用于 loglikelihood 打分")


def read_eot_token_id(hf_dir):
    cfg = json.load(open(os.path.join(hf_dir, "config.json"), encoding="utf-8"))
    eos = cfg.get("eos_token_id")
    if isinstance(eos, (list, tuple)):
        eos = eos[0]
    if eos is None:
        raise SystemExit("FAIL: config.json 无 eos_token_id，无法确定 eot_token_id")
    return int(eos)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", default="http://127.0.0.1:8080")
    ap.add_argument("--hf-dir", required=True, help="仅用于读 eos_token_id 与元信息")
    ap.add_argument("--output", required=True)
    ap.add_argument("--tasks", default=DEFAULT_TASKS)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--num-fewshot", type=int, default=0)
    ap.add_argument("--parallel", type=int, default=2, help="并发 slot 数（= llama-server --parallel）")
    ap.add_argument("--batch-size", type=int, default=32, help="lm_eval 每次提交的请求数")
    ap.add_argument("--max-length", type=int, default=2048)
    ap.add_argument("--timeout", type=int, default=600)
    ap.add_argument("--gguf", default="", help="可选，仅写入 meta 便于追溯")
    ap.add_argument("--log-samples", action="store_true")
    ap.add_argument("--samples", default=None, help='JSON string: {"task_name": [doc_idx,...]}')
    args = ap.parse_args()

    samples_dict = None
    if args.samples:
        samples_dict = json.loads(args.samples)
        print(f"[gguf] samples={samples_dict}", file=sys.stderr)

    task_list = [t.strip() for t in args.tasks.split(",") if t.strip()]
    os.makedirs(args.output, exist_ok=True)

    lm = GGUFServerLM(
        base_url=args.base_url,
        eot_token_id=read_eot_token_id(args.hf_dir),
        parallel=args.parallel,
        max_length=args.max_length,
        timeout=args.timeout,
        batch_size=args.batch_size,
    )

    print(f"[gguf] base_url={args.base_url}", file=sys.stderr)
    print(f"[gguf] tasks={task_list} limit={args.limit} parallel={args.parallel}", file=sys.stderr)
    t0 = time.time()
    results = simple_evaluate(
        model=lm,
        tasks=task_list,
        num_fewshot=args.num_fewshot,
        limit=args.limit,
        samples=samples_dict,
        batch_size=args.batch_size,
        log_samples=args.log_samples,
    )
    elapsed = time.time() - t0
    if not results:
        raise SystemExit("FAIL: simple_evaluate 返回空结果")

    result_file = os.path.join(args.output, "results.json")
    with open(result_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)

    meta = {
        "backend": "llama.cpp/llama-server (logit_bias teacher forcing)",
        "base_url": args.base_url,
        "hf_dir": args.hf_dir,
        "gguf": args.gguf,
        "tasks": task_list,
        "limit": args.limit,
        "num_fewshot": args.num_fewshot,
        "parallel": args.parallel,
        "batch_size": args.batch_size,
        "max_length": args.max_length,
        "n_token_requests": lm.n_token_requests,
        "n_docs_scored": lm.n_docs,
        "n_truncated_docs": lm.n_truncated,
        "elapsed_sec": round(elapsed, 2),
        "sec_per_token_request": (
            round(elapsed / lm.n_token_requests, 4) if lm.n_token_requests else None
        ),
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    with open(os.path.join(args.output, "meta.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 64, file=sys.stderr)
    print("EVALUATION RESULTS SUMMARY (GGUF/llama.cpp)", file=sys.stderr)
    print("=" * 64, file=sys.stderr)
    for task, tv in results.get("results", {}).items():
        for metric, value in tv.items():
            if metric.startswith("_"):
                continue
            if isinstance(value, (int, float)):
                print(f"  {task}/{metric}: {value:.4f}", file=sys.stderr)
            else:
                print(f"  {task}/{metric}: {value}", file=sys.stderr)
    print("=" * 64, file=sys.stderr)
    print(
        f"[gguf] elapsed={elapsed:.1f}s token_requests={lm.n_token_requests} "
        f"docs={lm.n_docs} s/req={meta['sec_per_token_request']}",
        file=sys.stderr,
    )
    print(f"[gguf] results -> {result_file}", file=sys.stderr)
    print(f"[gguf] meta    -> {os.path.join(args.output, 'meta.json')}", file=sys.stderr)


if __name__ == "__main__":
    main()




#!/usr/bin/env python3
"""Custom lm_eval model for llama.cpp server using per-token logprob scoring.

Problem: llama-server doesn't support echo=True (returning prompt token logprobs).
Solution: For each (context, continuation) pair, tokenize separately, then for each
continuation token, send the prefix as token IDs and look up the actual token's
logprob in the response's top_logprobs.

Usage:
  CUDA_VISIBLE_DEVICES="" python llamacpp_pertoken_lmeval.py \
    --base_url http://127.0.0.1:30012 \
    --tasks sciq,piqa --limit 100 \
    --output /path/to/results.json
"""
import sys, os, json, time, argparse, requests
from typing import List, Tuple

sys.path = [p for p in sys.path if "/dev/shm" not in p]
for k in list(sys.modules):
    if k.startswith("__editable__"):
        del sys.modules[k]

os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")
os.environ.setdefault("HF_DATASETS_OFFLINE", "1")
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("HF_DATASETS_CACHE", "/nas_train/app.e0031982/hf_cache")
os.environ.setdefault("HF_HOME", "/nas_train/app.e0031982/.cache")

import lm_eval
from lm_eval.api.model import LM
from lm_eval.api.registry import register_model


@register_model("llamacpp_pertoken")
class LlamaCppPerTokenLM(LM):
    """lm_eval model that scores via per-token logprob requests to llama-server."""

    def __init__(self, base_url=None, n_probs=50, max_length=2048, **kwargs):
        super().__init__()
        self.base_url = base_url.rstrip("/")
        assert self.base_url, "must pass base_url"
        self.n_probs = n_probs
        self.max_length = max_length
        r = requests.get(f"{self.base_url}/health", timeout=10)
        r.raise_for_status()
        print(f"[llamacpp_pertoken] connected to {self.base_url}, n_probs={n_probs}",
              file=sys.stderr)

    def _tokenize(self, text: str) -> List[int]:
        r = requests.post(f"{self.base_url}/tokenize",
                          json={"content": text}, timeout=30)
        r.raise_for_status()
        return r.json().get("tokens", [])

    def _score_token(self, prefix_tokens: List[int], target_id: int) -> Tuple[float, bool]:
        if not prefix_tokens:
            return -15.0, False
        r = requests.post(f"{self.base_url}/completion",
                          json={"prompt": prefix_tokens, "n_predict": 1,
                                "n_probs": self.n_probs,
                                "temperature": 0.0, "seed": 42}, timeout=120)
        r.raise_for_status()
        data = r.json()
        cp = data.get("completion_probabilities", [])
        if not cp:
            return -15.0, False
        entry = cp[0]
        is_greedy = (entry.get("id") == target_id)
        for tp in entry.get("top_logprobs", []):
            if tp.get("id") == target_id:
                return tp.get("logprob", -15.0), is_greedy
        if is_greedy:
            return entry.get("logprob", -15.0), True
        return -15.0, False

    def _find_split(self, ctx_tokens: List[int], full_tokens: List[int]) -> int:
        split = 0
        for i in range(min(len(ctx_tokens), len(full_tokens))):
            if ctx_tokens[i] == full_tokens[i]:
                split = i + 1
            else:
                break
        return max(split, 0)

    def loglikelihood(self, requests, disable_tqdm: bool = False):
        if not requests:
            return []
        from tqdm import tqdm
        res = []
        iterator = tqdm([req.args for req in requests],
                        disable=disable_tqdm, desc="loglikelihood")
        for context, continuation in iterator:
            ctx_tokens = self._tokenize(context)
            full_tokens = self._tokenize(context + continuation)
            split = self._find_split(ctx_tokens, full_tokens)
            cont_tokens = full_tokens[split:]
            if not cont_tokens:
                res.append((0.0, True))
                continue
            logprob_sum = 0.0
            is_greedy = True
            for i, tok_id in enumerate(cont_tokens):
                prefix = full_tokens[:split + i]
                lp, greedy = self._score_token(prefix, tok_id)
                logprob_sum += lp
                if not greedy:
                    is_greedy = False
            res.append((logprob_sum, is_greedy))
        return res

    def loglikelihood_rolling(self, requests, disable_tqdm: bool = False):
        return []

    def generate_until(self, requests, disable_tqdm: bool = False):
        if not requests:
            return []
        from tqdm import tqdm
        res = []
        iterator = tqdm([req.args for req in requests],
                        disable=disable_tqdm, desc="generate_until")
        for request in iterator:
            inp, request_args = request
            until = request_args.get("until", ["</s>"])
            max_gen = request_args.get("max_gen_toks", 256)
            r = requests.post(f"{self.base_url}/completion",
                              json={"prompt": inp, "n_predict": max_gen,
                                    "temperature": 0.0, "seed": 42,
                                    "stop": until}, timeout=300)
            r.raise_for_status()
            res.append(r.json().get("content", "").strip())
        return res


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base_url", required=True)
    parser.add_argument("--tasks", default="sciq,piqa")
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--n_probs", type=int, default=50)
    parser.add_argument("--num_fewshot", type=int, default=0)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    lm = LlamaCppPerTokenLM(base_url=args.base_url, n_probs=args.n_probs)
    task_list = [t.strip() for t in args.tasks.split(",")]
    print(f"[llamacpp_pertoken] tasks={task_list} limit={args.limit}", file=sys.stderr)

    t0 = time.time()
    results = lm_eval.simple_evaluate(
        model=lm, tasks=task_list, num_fewshot=args.num_fewshot,
        limit=args.limit, log_samples=False)
    t_eval = time.time() - t0
    print(f"[llamacpp_pertoken] eval done in {t_eval:.1f}s", file=sys.stderr)

    with open(args.output, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"[llamacpp_pertoken] results saved to {args.output}", file=sys.stderr)

    print("\n" + "=" * 60, file=sys.stderr)
    print("EVALUATION RESULTS SUMMARY", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    for task_name, task_results in results.get("results", {}).items():
        for metric, value in task_results.items():
            if not metric.startswith("_"):
                if isinstance(value, float):
                    print(f"  {task_name}/{metric}: {value:.4f}", file=sys.stderr)
                else:
                    print(f"  {task_name}/{metric}: {value}", file=sys.stderr)
    print("=" * 60, file=sys.stderr)


if __name__ == "__main__":
    main()


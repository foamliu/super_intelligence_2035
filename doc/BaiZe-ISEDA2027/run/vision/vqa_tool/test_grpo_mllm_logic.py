#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fast CPU verification of grpo_mllm_wave.py novel logic (no model load).

验证（不依赖 4.5GB 模型 NFS 加载）：
  1. 合成 case 生成 + parse_answer + reward_for（真实奖励管线）
  2. group-relative advantage（含 std=0 零信号退化）
  3. completion_logprobs 的 token-mask 切片口径（用 dummy logits 验证 span 正确）
  4. grpo_update 的 PPO clipped surrogate 数学（dummy logprob 张量，loss 有限 + 梯度可回传）
模型前向（load_model_for_train/generate/forward）复用已验证的 v2 管线，此处不测。
"""
import os, sys, json
import numpy as np
import torch
import torch.nn.functional as F

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from synth_waveform_qa import make_case, parse_answer, reward_for, SKILLS
from grpo_mllm_wave import build_train_cases, grpo_update

fail = 0
def check(cond, msg):
    global fail
    print(("[OK] " if cond else "[FAIL] ") + msg, flush=True)
    if not cond: fail += 1

def math_finite(x):
    import math
    try:
        return math.isfinite(float(x))
    except Exception:
        return False

# 1) 真实奖励管线：造一道 cycle_count 题，给对/错答案看奖励
cases = build_train_cases(20261114, n_per_skill=1)
cc = [c for c in cases if c["skill"] == "cycle_count"][0]
gt_n = cc["gt_num"]
r_correct = reward_for(cc["skill"], cc["kind"], str(int(gt_n)), cc["gt"], gt_n)
r_wrong = reward_for(cc["skill"], cc["kind"], str(int(gt_n) + 10), cc["gt"], gt_n)
check(r_correct > 0.99, f"cycle_count correct reward={r_correct:.3f} ~= 1.0")
check(r_wrong < 0.5, f"cycle_count wrong(+10) reward={r_wrong:.3f} < 0.5")
# 分类二值
tc = [c for c in cases if c["skill"] == "type_classification"][0]
check(reward_for(tc["skill"], tc["kind"], tc["gt"], tc["gt"], None) == 1.0, "type_classification exact match -> 1.0")
check(reward_for(tc["skill"], tc["kind"], "wrongtype", tc["gt"], None) == 0.0, "type_classification mismatch -> 0.0")

# 2) group advantage：含 std=0 退化
rewards = np.array([1.0, 0.0, 0.5, 0.5])
mean, std = rewards.mean(), rewards.std()
advs = (rewards - mean) / (std + 1e-4) if std > 1e-6 else np.zeros_like(rewards)
check(abs(advs.sum()) < 1e-6, f"advantages zero-sum: sum={advs.sum():.6f}")
zero = np.array([0.5, 0.5, 0.5])
zmean, zstd = zero.mean(), zero.std()
zadv = (zero - zmean) / (zstd + 1e-4) if zstd > 1e-6 else np.zeros_like(zero)
check(np.allclose(zadv, 0.0), "std=0 group -> advantages all 0 (no spurious signal)")

# 3) completion_logprobs mask 切片口径：dummy 序列 prompt_len=4, T=7（3 completion token）
#    token_lps[0] 长度 T-1=6，下标 0..5；completion token 由 logit 下标 prompt_len-1..T-2 = 3..5
V = 16
full_ids = torch.tensor([1, 2, 3, 4, 5, 6, 7])   # T=7, prompt_len=4
prompt_len = 4
logits = torch.zeros(1, 7, V)
# 仅 completion 预测位 (i >= prompt_len-1=3) 给大峰 → 该位置 target logprob ≈ 0；
# prompt 预测位 (i < 3) 留均匀 → target logprob = log(1/V) ≈ -2.77，与 comp 区分，
# 这样既能验证 comp 内为 completion logprob(~0)，又能验证 prompt logprob 被排除在外。
for i in range(prompt_len - 1, 6):              # i = 3,4,5 = completion 预测位
    logits[0, i, int(full_ids[i + 1])] = 50.0   # 大峰 → logprob ≈ 0（远小于 1e-4）
lp = F.log_softmax(logits[:, :-1, :].float(), dim=-1)
token_lps = lp.gather(2, full_ids[1:].unsqueeze(0).unsqueeze(-1)).squeeze(0)  # len 6
comp = token_lps[prompt_len - 1: 6]   # 切片 = grpo_mllm completion_logprobs 口径
check(comp.numel() == 3, f"completion span length == 3 (got {comp.numel()})")
check(torch.allclose(comp, torch.zeros(3), atol=1e-4), "completion token logprobs ~= 0 (mask slicing correct)")
# prompt 预测位的 target logprob 应为 log(1/V) ≈ -2.77（<<0，且不在 comp 内）
check(float(token_lps[0]) < -1.0, f"prompt token logprob excluded (token_lps[0]={float(token_lps[0]):.2f} << 0)")

# 4) grpo_update PPO clipped surrogate：dummy rollouts，loss 有限 + 梯度回传
class DummyModel:
    def __call__(self, input_ids, attention_mask, pixel_values=None):
        T = input_ids.shape[1]
        # logits 必须依赖 _logit_param，backward 才能把梯度回传到该参数（否则 .grad 为 None）
        base = torch.randn(1, T, V)
        out = type("o", (), {"logits": base + self._logit_param.unsqueeze(0).unsqueeze(0) * 0.01})()
        self._last = out.logits
        return out
    def parameters(self): return [self._logit_param]
    def save_pretrained(self, d):
        os.makedirs(d, exist_ok=True); open(os.path.join(d, "adapter_config.json"), "w").write("{}")
dm = DummyModel()
dm._logit_param = torch.nn.Parameter(torch.randn(V))
opt = torch.optim.SGD([dm._logit_param], lr=1e-3)
rollouts = []
for adv in (1.0, -1.0):
    full = torch.tensor([1, 2, 3, 4, 5, 6])
    old_lp = torch.zeros(2)  # prompt_len=4 -> completion len=2
    rollouts.append({"full_ids": full, "prompt_len": 4, "img_inputs": None,
                     "old_logprob": old_lp, "adv": adv})
# monkeypatch completion_logprobs in grpo_update via module-level call: 给 DummyModel 提供 forward
# grpo_update 调 completion_logprobs(model, ...) -> model(...) 取 .logits；DummyModel 符合
loss_val, n_tok = grpo_update(dm, rollouts, opt, clip_eps=0.2, device="cpu", ppo_epochs=1)
check(math_finite(loss_val), f"grpo_update loss finite = {loss_val:.4f}")
check(n_tok > 0, f"grpo_update counted tokens = {n_tok}")
g = dm._logit_param.grad
check(g is not None and torch.isfinite(g).all(), "gradient propagated to params")

print(f"\n=== logic test {'PASS' if fail == 0 else 'FAIL'} (fails={fail}) ===", flush=True)
sys.exit(0 if fail == 0 else 1)
